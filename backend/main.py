
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Literal
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
import sqlite3
import httpx
import time
import asyncio


# ==========================================
# CONFIGURATION
# ==========================================

MONITOR_INTERVAL = 60

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "api_history.db"


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS request_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                success INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS monitored_apis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_id INTEGER NOT NULL,
                status_code INTEGER,
                response_time REAL,
                is_online INTEGER NOT NULL,
                checked_at TEXT NOT NULL,
                FOREIGN KEY(api_id) REFERENCES monitored_apis(id)
            )
        """)

        # NEW: Persistent alert history

        connection.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_id INTEGER NOT NULL,
                api_name TEXT NOT NULL,
                api_url TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(api_id) REFERENCES monitored_apis(id)
            )
        """)


initialize_database()


# ==========================================
# DATABASE HELPERS
# ==========================================

def save_history(url, method, status_code, response_time, success):

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute("""
            INSERT INTO request_history
            (url, method, status_code, response_time, success, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            url,
            method,
            status_code,
            response_time,
            int(success),
            datetime.now().isoformat(timespec="seconds")
        ))


# ==========================================
# MONITORING ENGINE
# ==========================================

async def perform_monitor_check(api):

    start_time = time.perf_counter()

    status_code = None
    is_online = False
    error_message = None

    try:

        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True
        ) as client:

            response = await client.get(api["url"])

        status_code = response.status_code
        is_online = response.is_success

        if not is_online:
            error_message = response.reason_phrase or "HTTP error"

    except httpx.RequestError as error:

        is_online = False
        error_message = str(error)

    response_time = round(
        (time.perf_counter() - start_time) * 1000,
        2
    )

    checked_at = datetime.now().isoformat(timespec="seconds")

    # ======================================
    # SAVE CHECK AND DETECT STATUS CHANGES
    # ======================================

    with sqlite3.connect(DB_PATH, timeout=10) as connection:

        # Prevent simultaneous checks from creating duplicate alerts.
        connection.execute("BEGIN IMMEDIATE")

        previous = connection.execute("""
            SELECT is_online
            FROM monitoring_history
            WHERE api_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (api["id"],)).fetchone()

        connection.execute("""
            INSERT INTO monitoring_history
            (api_id, status_code, response_time, is_online, checked_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            api["id"],
            status_code,
            response_time,
            int(is_online),
            checked_at
        ))

        event_type = None
        message = None

        previous_status = previous[0] if previous else None

        # First check: create an alert only if the API is offline.
        if previous_status is None and not is_online:

            event_type = "DOWN"

        # Previously online, now offline.
        elif previous_status == 1 and not is_online:

            event_type = "DOWN"

        # Previously offline, now online.
        elif previous_status == 0 and is_online:

            event_type = "RECOVERED"

        if event_type == "DOWN":

            if status_code is not None:
                message = (
                    f"{api['name']} is DOWN. "
                    f"HTTP status code: {status_code}."
                )
            else:
                message = (
                    f"{api['name']} is DOWN. "
                    f"Connection failed: {error_message or 'Unknown error'}"
                )

        elif event_type == "RECOVERED":

            message = (
                f"{api['name']} has RECOVERED "
                f"and is responding successfully."
            )

        # Save an alert only when a meaningful status transition occurs.
        if event_type:

            connection.execute("""
                INSERT INTO monitoring_alerts
                (
                    api_id,
                    api_name,
                    api_url,
                    event_type,
                    status_code,
                    response_time,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api["id"],
                api["name"],
                api["url"],
                event_type,
                status_code,
                response_time,
                message,
                checked_at
            ))

            print(
                f"ALERT: {event_type} - {api['name']}"
            )

    return {
        "api_id": api["id"],
        "name": api["name"],
        "url": api["url"],
        "status": "Online" if is_online else "Offline",
        "status_code": status_code,
        "response_time_ms": response_time,
        "checked_at": checked_at,
        "alert_generated": event_type is not None,
        "alert_type": event_type
    }


async def run_monitoring_cycle():

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        apis = connection.execute("""
            SELECT * FROM monitored_apis
        """).fetchall()

    for api in apis:

        try:

            await perform_monitor_check(api)

        except Exception as error:

            print(
                f"Automatic monitoring error for "
                f"{api['name']}: {error}"
            )


async def automatic_monitoring():

    print("Automatic monitoring service started.")

    while True:

        await run_monitoring_cycle()

        print(
            f"Monitoring cycle completed. "
            f"Next check in {MONITOR_INTERVAL} seconds."
        )

        await asyncio.sleep(MONITOR_INTERVAL)


# ==========================================
# APPLICATION LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    monitoring_task = asyncio.create_task(
        automatic_monitoring()
    )

    yield

    monitoring_task.cancel()

    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass

    print("Automatic monitoring service stopped.")


app = FastAPI(
    title="API Sentinel",
    description="API Testing and Monitoring Platform",
    version="3.1.0",
    lifespan=lifespan
)


# ==========================================
# REQUEST MODELS
# ==========================================

class APIRequest(BaseModel):

    url: AnyHttpUrl
    method: Literal["GET", "POST", "PUT", "DELETE"] = "GET"
    headers: dict = Field(default_factory=dict)
    body: dict | None = None


class MonitorRequest(BaseModel):

    name: str
    url: AnyHttpUrl


# ==========================================
# HOME AND HEALTH
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to API Sentinel!",
        "status": "Running",
        "version": "3.1.0"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "API Sentinel Backend"
    }


# ==========================================
# API TESTER
# ==========================================

@app.post("/api/test")
async def test_api(request: APIRequest):

    start_time = time.perf_counter()
    url = str(request.url)

    try:

        async with httpx.AsyncClient(timeout=15.0) as client:

            response = await client.request(
                method=request.method,
                url=url,
                headers=request.headers,
                json=request.body
            )

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        response_body = response.text
        truncated = len(response_body) > 10000

        save_history(
            url,
            request.method,
            response.status_code,
            response_time,
            response.is_success
        )

        return {
            "url": url,
            "method": request.method,
            "status_code": response.status_code,
            "success": response.is_success,
            "response_time_ms": response_time,
            "headers": dict(response.headers),
            "response_body": response_body[:10000],
            "body_truncated": truncated
        }

    except httpx.RequestError as error:

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        save_history(
            url,
            request.method,
            502,
            response_time,
            False
        )

        raise HTTPException(
            status_code=502,
            detail=f"Request failed: {str(error)}"
        )


# ==========================================
# REQUEST HISTORY
# ==========================================

@app.get("/api/history")
def get_history():

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT * FROM request_history
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    return {
        "total": len(rows),
        "history": [dict(row) for row in rows]
    }


@app.delete("/api/history")
def clear_history():

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute("DELETE FROM request_history")

    return {
        "message": "Request history cleared successfully"
    }


# ==========================================
# ADD API FOR MONITORING
# ==========================================

@app.post("/monitor/add")
def add_monitored_api(request: MonitorRequest):

    name = request.name.strip()
    url = str(request.url)

    if not name:

        raise HTTPException(
            status_code=400,
            detail="API name cannot be empty"
        )

    try:

        with sqlite3.connect(DB_PATH) as connection:

            cursor = connection.execute("""
                INSERT INTO monitored_apis
                (name, url, created_at)
                VALUES (?, ?, ?)
            """, (
                name,
                url,
                datetime.now().isoformat(timespec="seconds")
            ))

            api_id = cursor.lastrowid

        return {
            "message": "API added for monitoring",
            "api_id": api_id,
            "name": name,
            "url": url
        }

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=409,
            detail="This API URL is already being monitored"
        )


# ==========================================
# LIST MONITORED APIS
# ==========================================

@app.get("/monitor/list")
def list_monitored_apis():

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT * FROM monitored_apis
            ORDER BY id DESC
        """).fetchall()

    return {
        "total": len(rows),
        "apis": [dict(row) for row in rows]
    }


# ==========================================
# MANUAL API STATUS CHECK
# ==========================================

@app.post("/monitor/check/{api_id}")
async def check_monitored_api(api_id: int):

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        api = connection.execute("""
            SELECT * FROM monitored_apis
            WHERE id = ?
        """, (api_id,)).fetchone()

    if api is None:

        raise HTTPException(
            status_code=404,
            detail="Monitored API not found"
        )

    return await perform_monitor_check(api)


# ==========================================
# MONITORING HISTORY
# ==========================================

@app.get("/monitor/history/{api_id}")
def get_monitoring_history(api_id: int):

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        api = connection.execute("""
            SELECT id FROM monitored_apis
            WHERE id = ?
        """, (api_id,)).fetchone()

        if api is None:

            raise HTTPException(
                status_code=404,
                detail="Monitored API not found"
            )

        rows = connection.execute("""
            SELECT * FROM monitoring_history
            WHERE api_id = ?
            ORDER BY id DESC
            LIMIT 100
        """, (api_id,)).fetchall()

        total = connection.execute("""
            SELECT COUNT(*) FROM monitoring_history
            WHERE api_id = ?
        """, (api_id,)).fetchone()[0]

    return {
        "api_id": api_id,
        "total_checks": total,
        "history": [dict(row) for row in rows]
    }


# ==========================================
# NEW: FAILURE AND RECOVERY ALERT HISTORY
# ==========================================

@app.get("/monitor/alerts")
def get_monitoring_alerts(
    api_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=200)
):

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        if api_id is not None:

            rows = connection.execute("""
                SELECT * FROM monitoring_alerts
                WHERE api_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (api_id, limit)).fetchall()

            total = connection.execute("""
                SELECT COUNT(*) FROM monitoring_alerts
                WHERE api_id = ?
            """, (api_id,)).fetchone()[0]

        else:

            rows = connection.execute("""
                SELECT * FROM monitoring_alerts
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

            total = connection.execute("""
                SELECT COUNT(*) FROM monitoring_alerts
            """).fetchone()[0]

    return {
        "total_alerts": total,
        "alerts": [dict(row) for row in rows]
    }


# ==========================================
# UPTIME AND PERFORMANCE SUMMARY
# ==========================================

@app.get("/monitor/summary")
def monitoring_summary():

    with sqlite3.connect(DB_PATH) as connection:

        connection.row_factory = sqlite3.Row

        apis = connection.execute("""
            SELECT * FROM monitored_apis
            ORDER BY id DESC
        """).fetchall()

        summaries = []

        for api in apis:

            stats = connection.execute("""
                SELECT
                    COUNT(*) AS total_checks,
                    SUM(is_online) AS successful_checks,
                    AVG(response_time) AS average_response_time
                FROM monitoring_history
                WHERE api_id = ?
            """, (api["id"],)).fetchone()

            latest = connection.execute("""
                SELECT status_code, is_online, checked_at
                FROM monitoring_history
                WHERE api_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (api["id"],)).fetchone()

            total = stats["total_checks"] or 0
            successful = stats["successful_checks"] or 0

            uptime = (
                (successful / total) * 100
                if total > 0 else 0
            )

            summaries.append({
                "api_id": api["id"],
                "name": api["name"],
                "url": api["url"],
                "total_checks": total,
                "successful_checks": successful,
                "failed_checks": total - successful,
                "uptime_percentage": round(uptime, 2),
                "average_response_time_ms": round(
                    stats["average_response_time"] or 0,
                    2
                ),
                "last_status": (
                    "Online" if latest["is_online"] else "Offline"
                ) if latest else "Not checked",
                "last_status_code": (
                    latest["status_code"] if latest else None
                ),
                "last_checked": (
                    latest["checked_at"] if latest else None
                )
            })

    return {
        "monitoring_interval_seconds": MONITOR_INTERVAL,
        "total_monitored_apis": len(summaries),
        "apis": summaries
    }


# ==========================================
# DELETE MONITORED API
# ==========================================

@app.delete("/monitor/delete/{api_id}")
def delete_monitored_api(api_id: int):

    with sqlite3.connect(DB_PATH) as connection:

        exists = connection.execute("""
            SELECT id FROM monitored_apis
            WHERE id = ?
        """, (api_id,)).fetchone()

        if exists is None:

            raise HTTPException(
                status_code=404,
                detail="Monitored API not found"
            )

        # Remove associated history and alerts.

        connection.execute("""
            DELETE FROM monitoring_alerts
            WHERE api_id = ?
        """, (api_id,))

        connection.execute("""
            DELETE FROM monitoring_history
            WHERE api_id = ?
        """, (api_id,))

        connection.execute("""
            DELETE FROM monitored_apis
            WHERE id = ?
        """, (api_id,))

    return {
        "message": "Monitored API deleted successfully"
    }
