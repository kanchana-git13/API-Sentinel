
import streamlit as st
import httpx
import json
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURATION
# ==========================================

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="API Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LIGHT THEME DESIGN
# ==========================================

st.markdown("""
<style>

/* MAIN APPLICATION */

.stApp {
    background-color: #f5f7fb;
    color: #172033;
}

[data-testid="stHeader"] {
    background-color: #f5f7fb;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #ffffff;
}

[data-testid="stSidebar"] h2 {
    color: #1e40af;
    font-weight: 800;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #334155;
}

/* SIDEBAR NAVIGATION */

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 9px;
    padding: 10px 12px;
    color: #334155 !important;
    font-weight: 600;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #dbeafe;
    border-color: #93c5fd;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
    color: #ffffff !important;
}

/* HEADINGS */

h1, h2, h3, h4 {
    color: #172554 !important;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #1d4ed8;
    margin-bottom: 0;
}

.subtitle {
    color: #64748b;
    font-size: 15px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 21px;
    font-weight: 700;
    color: #1e293b;
    margin-top: 20px;
    margin-bottom: 12px;
}

/* TEXT */

p, label, .stMarkdown {
    color: #334155;
}

[data-testid="stCaptionContainer"] {
    color: #64748b;
}

/* METRIC CARDS */

div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}

div[data-testid="stMetricLabel"] {
    color: #64748b !important;
}

div[data-testid="stMetricLabel"] p {
    color: #64748b !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #172554 !important;
    font-weight: 750;
}

div[data-testid="stMetricDelta"] {
    color: #475569 !important;
}

/* CUSTOM METRIC CARDS */

.metric-card {
    background-color: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 12px;
    padding: 20px;
    min-height: 115px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}

.metric-label {
    color: #64748b;
    font-size: 14px;
}

.metric-value {
    color: #1e40af;
    font-size: 28px;
    font-weight: 750;
    margin-top: 8px;
}

/* BUTTONS */

.stButton button,
.stFormSubmitButton button {
    border-radius: 8px;
    font-weight: 600;
    border: 1px solid #cbd5e1;
    transition: all 0.2s ease;
}

.stButton button:not([kind="primary"]),
.stFormSubmitButton button:not([kind="primary"]) {
    background-color: #ffffff;
    color: #1e40af;
}

.stButton button:hover {
    border-color: #2563eb;
    color: #1d4ed8;
}

/* PRIMARY BUTTONS */

.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
}

.stButton button[kind="primary"]:hover,
.stFormSubmitButton button[kind="primary"]:hover {
    background-color: #1d4ed8;
    color: #ffffff;
}

/* INPUT FIELDS */

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stNumberInput input {
    background-color: #ffffff !important;
    color: #172033 !important;
    border-color: #cbd5e1 !important;
    border-radius: 8px;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb;
}

/* SELECTBOX TEXT */

[data-baseweb="select"] span {
    color: #172033 !important;
}

/* CONTAINERS */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff;
    border-color: #dbe3ef !important;
    border-radius: 12px;
}

/* EXPANDERS */

[data-testid="stExpander"] {
    background-color: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 10px;
}

[data-testid="stExpander"] summary {
    color: #1e293b;
    font-weight: 600;
}

/* TABLES */

[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border: 1px solid #dbe3ef;
    border-radius: 10px;
}

/* ALERTS */

[data-testid="stAlert"] {
    border-radius: 10px;
}

/* DIVIDERS */

hr {
    border-color: #e2e8f0;
}

/* CHART BACKGROUND */

[data-testid="stPlotlyChart"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 10px;
}

/* JSON AND CODE */

[data-testid="stJson"],
.stCodeBlock {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

/* SPINNER */

.stSpinner > div {
    border-top-color: #2563eb !important;
}

/* LINKS */

a {
    color: #2563eb !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CHART THEME HELPER
# ==========================================

def apply_light_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="Arial",
            color="#334155",
            size=13
        ),
        title_font=dict(
            color="#172554",
            size=18
        ),
        legend=dict(
            font=dict(color="#334155")
        ),
        margin=dict(l=30, r=30, t=65, b=30)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e9eef5",
        zerolinecolor="#cbd5e1",
        color="#475569"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e9eef5",
        zerolinecolor="#cbd5e1",
        color="#475569"
    )

    return fig


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_backend_health():
    try:
        response = httpx.get(
            f"{BACKEND_URL}/health",
            timeout=3
        )
        return response.is_success
    except httpx.RequestError:
        return False


def get_request_history():
    response = httpx.get(
        f"{BACKEND_URL}/api/history",
        timeout=10
    )
    response.raise_for_status()
    return response.json()["history"]


def get_monitored_apis():
    response = httpx.get(
        f"{BACKEND_URL}/monitor/list",
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    if isinstance(data, list):
        return data

    for key in ["monitored_apis", "apis", "items"]:
        if key in data:
            return data[key]

    return []


def get_monitoring_history(api_id):
    response = httpx.get(
        f"{BACKEND_URL}/monitor/history/{api_id}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_monitoring_summary():
    response = httpx.get(
        f"{BACKEND_URL}/monitor/summary",
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_alert_history(limit=200):
    response = httpx.get(
        f"{BACKEND_URL}/monitor/alerts",
        params={"limit": limit},
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown("## 🛡️ API SENTINEL")

    st.caption("API Testing & Monitoring Platform")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "API Tester",
            "Request History",
            "Analytics",
            "API Monitoring",
            "Alert History"
        ]
    )

    st.divider()

    st.markdown("### Backend Status")

    if get_backend_health():
        st.success("● Backend Online")
    else:
        st.error("● Backend Offline")

    st.caption("Version 4.0.0")


# ==========================================
# DASHBOARD - LIVE MONITORING
# ==========================================

if page == "Dashboard":

    @st.fragment(run_every="60s")
    def live_dashboard():

        st.markdown(
            '<div class="main-title">API Sentinel</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Live API monitoring command center</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "🔄 Dashboard refreshes automatically every 60 seconds."
        )

        if st.button("🔄 Refresh Dashboard"):
            st.rerun()

        try:

            history = get_request_history()

            if history:

                df = pd.DataFrame(history)

                total = len(df)
                successful = int(df["success"].sum())
                failed = total - successful

                success_rate = (
                    successful / total * 100
                    if total else 0
                )

                avg_time = df["response_time"].mean()

            else:

                total = 0
                successful = 0
                failed = 0
                success_rate = 0
                avg_time = 0

            st.subheader("📊 Request Overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Total Requests", total)
            c2.metric("Successful", successful)
            c3.metric("Failed", failed)
            c4.metric("Success Rate", f"{success_rate:.1f}%")

            st.divider()

            st.subheader("📡 Live API Monitoring")

            summary = get_monitoring_summary()

            apis = summary.get("apis", [])

            if apis:

                total_apis = len(apis)

                online = sum(
                    1 for api in apis
                    if api.get("last_status") == "Online"
                )

                offline = total_apis - online

                total_checks = sum(
                    api.get("total_checks", 0)
                    for api in apis
                )

                successful_checks = sum(
                    api.get("successful_checks", 0)
                    for api in apis
                )

                overall_uptime = (
                    successful_checks / total_checks * 100
                    if total_checks else 0
                )

                m1, m2, m3, m4 = st.columns(4)

                m1.metric("Monitored APIs", total_apis)
                m2.metric("🟢 Online", online)
                m3.metric("🔴 Offline", offline)
                m4.metric("Overall Uptime", f"{overall_uptime:.1f}%")

                if offline > 0:

                    st.error(
                        f"⚠️ Alert: {offline} monitored API(s) "
                        "are currently offline!"
                    )

                else:

                    st.success(
                        "All monitored APIs are currently online."
                    )

                st.divider()

                st.subheader("🌐 Individual API Status")

                for api in apis:

                    with st.container(border=True):

                        col1, col2, col3 = st.columns([3, 1, 1])

                        with col1:

                            st.markdown(f"### {api['name']}")

                            st.caption(api["url"])

                        with col2:

                            if api.get("last_status") == "Online":
                                st.success("🟢 ONLINE")
                            else:
                                st.error("🔴 OFFLINE")

                        with col3:

                            st.metric(
                                "Uptime",
                                f"{api.get('uptime_percentage', 0):.1f}%"
                            )

                        a, b, c = st.columns(3)

                        a.metric(
                            "Average Response Time",
                            f"{api.get('average_response_time_ms', 0):.2f} ms"
                        )

                        b.metric(
                            "Total Checks",
                            api.get("total_checks", 0)
                        )

                        c.metric(
                            "HTTP Status",
                            api.get("last_status_code")
                            if api.get("last_status_code") is not None
                            else "N/A"
                        )

                        st.caption(
                            f"Last checked: {api.get('last_checked', 'N/A')}"
                        )

                st.divider()

                st.subheader("📈 API Uptime Comparison")

                uptime_df = pd.DataFrame([
                    {
                        "API": api["name"],
                        "Uptime (%)": api.get(
                            "uptime_percentage", 0
                        )
                    }
                    for api in apis
                ])

                fig1 = px.bar(
                    uptime_df,
                    x="API",
                    y="Uptime (%)",
                    color="Uptime (%)",
                    range_y=[0, 100],
                    title="Uptime Percentage by API",
                    color_continuous_scale="Blues"
                )

                fig1 = apply_light_chart(fig1)

                st.plotly_chart(
                    fig1,
                    use_container_width=True
                )

                st.subheader("⏱️ Response Time Trends")

                response_records = []

                for api in apis:

                    try:

                        monitor_data = get_monitoring_history(
                            api["api_id"]
                        )

                        for check in monitor_data.get("history", []):

                            response_records.append({
                                "API": api["name"],
                                "Checked At": check["checked_at"],
                                "Response Time (ms)": check["response_time"]
                            })

                    except httpx.RequestError:
                        continue

                if response_records:

                    response_df = pd.DataFrame(response_records)

                    response_df["Checked At"] = pd.to_datetime(
                        response_df["Checked At"]
                    )

                    response_df = response_df.sort_values(
                        "Checked At"
                    )

                    fig2 = px.line(
                        response_df,
                        x="Checked At",
                        y="Response Time (ms)",
                        color="API",
                        markers=True,
                        title="API Response Time Over Time"
                    )

                    fig2 = apply_light_chart(fig2)

                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Response-time history will appear "
                        "after monitoring checks."
                    )

            else:

                st.info(
                    "No APIs are being monitored yet. "
                    "Visit API Monitoring to add an API."
                )

            st.divider()

            st.subheader("📜 Recent API Requests")

            if history:

                recent_df = pd.DataFrame(history).head(5).copy()

                recent_df["success"] = recent_df["success"].map({
                    1: "Success",
                    0: "Failed"
                })

                st.dataframe(
                    recent_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No API requests recorded yet.")

        except httpx.RequestError as error:

            st.error(f"Backend connection error: {error}")

        except (KeyError, ValueError, TypeError) as error:

            st.error(f"Could not display dashboard data: {error}")

    live_dashboard()


# ==========================================
# API TESTER
# ==========================================

elif page == "API Tester":

    st.title("🚀 API Tester")

    st.caption(
        "Send HTTP requests and inspect API responses."
    )

    with st.container(border=True):

        st.subheader("Request Configuration")

        method = st.selectbox(
            "HTTP Method",
            ["GET", "POST", "PUT", "DELETE"]
        )

        url = st.text_input(
            "API Endpoint URL",
            placeholder="https://jsonplaceholder.typicode.com/posts/1"
        )

        headers_input = st.text_area(
            "Request Headers (JSON)",
            value="{}"
        )

        body_input = st.text_area(
            "Request Body (JSON)",
            value="{}"
        )

        send_request = st.button(
            "🚀 Send API Request",
            type="primary",
            use_container_width=True
        )

    if send_request:

        try:

            headers = json.loads(headers_input)

            body = (
                json.loads(body_input)
                if body_input.strip()
                else None
            )

            if not url.strip():

                st.error("Please enter an API URL.")

            elif not isinstance(headers, dict):

                st.error("Headers must be a JSON object.")

            elif body is not None and not isinstance(body, dict):

                st.error("Body must be a JSON object.")

            else:

                with st.spinner("Sending API request..."):

                    result = httpx.post(
                        f"{BACKEND_URL}/api/test",
                        json={
                            "url": url,
                            "method": method,
                            "headers": headers,
                            "body": body
                        },
                        timeout=20
                    )

                if result.is_success:

                    data = result.json()

                    if data["success"]:
                        st.success(
                            "API request completed successfully!"
                        )
                    else:
                        st.warning(
                            "The API returned an unsuccessful HTTP status."
                        )

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Status Code",
                        data["status_code"]
                    )

                    c2.metric(
                        "Response Time",
                        f'{data["response_time_ms"]} ms'
                    )

                    c3.metric(
                        "Result",
                        "Success" if data["success"] else "Failed"
                    )

                    st.markdown("### Response Body")

                    try:

                        response_json = json.loads(
                            data["response_body"]
                        )

                        st.json(response_json)

                    except (json.JSONDecodeError, TypeError):

                        st.code(data["response_body"])

                    st.markdown("### Response Headers")

                    st.json(data["headers"])

                    if data["body_truncated"]:
                        st.warning(
                            "Response body was truncated."
                        )

                else:

                    st.error(
                        f"Request failed: {result.text}"
                    )

        except json.JSONDecodeError:

            st.error(
                "Invalid JSON. Please check your headers and body."
            )

        except httpx.RequestError as error:

            st.error(f"Connection error: {error}")


# ==========================================
# REQUEST HISTORY
# ==========================================

elif page == "Request History":

    st.title("📜 Request History")

    st.caption(
        "Review previously executed API requests."
    )

    if st.button("🔄 Refresh History"):
        st.rerun()

    try:

        history = get_request_history()

        if history:

            df = pd.DataFrame(history)

            successful = int(df["success"].sum())
            failed = len(df) - successful

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Requests", len(df))
            c2.metric("Successful", successful)
            c3.metric("Failed", failed)

            st.divider()

            display_df = df.copy()

            display_df["success"] = display_df["success"].map({
                1: "Success",
                0: "Failed"
            })

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            if st.button(
                "🗑️ Clear History",
                type="secondary"
            ):

                delete_response = httpx.delete(
                    f"{BACKEND_URL}/api/history",
                    timeout=10
                )

                if delete_response.is_success:

                    st.success(
                        "History cleared successfully!"
                    )

                    st.rerun()

                else:

                    st.error("Could not clear history.")

        else:

            st.info(
                "No request history found. Test an API first."
            )

    except httpx.RequestError as error:

        st.error(
            f"Could not load request history: {error}"
        )


# ==========================================
# ANALYTICS
# ==========================================

elif page == "Analytics":

    st.title("📊 Performance Analytics")

    st.caption(
        "Understand your API performance and reliability."
    )

    if st.button("🔄 Refresh Analytics"):
        st.rerun()

    try:

        history = get_request_history()

        if history:

            df = pd.DataFrame(history)

            total = len(df)
            successful = int(df["success"].sum())
            failed = total - successful

            avg_time = df["response_time"].mean()

            success_rate = (
                successful / total * 100
            )

            st.markdown("### Performance Overview")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric("Total Requests", total)
            c2.metric("Successful", successful)
            c3.metric("Failed", failed)
            c4.metric("Avg Response", f"{avg_time:.2f} ms")
            c5.metric("Success Rate", f"{success_rate:.1f}%")

            st.divider()

            st.subheader("Request Success vs Failure")

            result_df = pd.DataFrame({
                "Result": ["Successful", "Failed"],
                "Requests": [successful, failed]
            })

            fig1 = px.bar(
                result_df,
                x="Result",
                y="Requests",
                color="Result",
                title="Successful and Failed Requests",
                color_discrete_map={
                    "Successful": "#16a34a",
                    "Failed": "#dc2626"
                }
            )

            fig1 = apply_light_chart(fig1)

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            st.subheader("HTTP Status Code Distribution")

            status_df = (
                df["status_code"]
                .value_counts()
                .rename_axis("Status Code")
                .reset_index(name="Count")
            )

            status_df["Status Code"] = (
                status_df["Status Code"].astype(str)
            )

            fig2 = px.pie(
                status_df,
                names="Status Code",
                values="Count",
                hole=0.45,
                title="Distribution of HTTP Status Codes"
            )

            fig2.update_layout(
                template="plotly_white",
                paper_bgcolor="#ffffff",
                font=dict(color="#334155")
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            st.subheader("Response Time History")

            time_df = df.sort_values("id")

            fig3 = px.line(
                time_df,
                x="id",
                y="response_time",
                markers=True,
                title="API Response Time in Milliseconds",
                labels={
                    "id": "Request ID",
                    "response_time": "Response Time (ms)"
                }
            )

            fig3 = apply_light_chart(fig3)

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

            st.subheader("Recent API Performance")

            st.dataframe(
                df[
                    [
                        "id",
                        "url",
                        "method",
                        "status_code",
                        "response_time",
                        "success",
                        "created_at"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No API history available. Test an API first."
            )

    except httpx.RequestError as error:

        st.error(
            f"Could not load analytics: {error}"
        )


# ==========================================
# API MONITORING
# ==========================================

elif page == "API Monitoring":

    st.title("📡 API Monitoring")

    st.caption(
        "Register APIs, check their availability, "
        "and track their monitoring history."
    )

    st.divider()

    st.subheader("➕ Add API to Monitor")

    with st.form(
        "add_monitor_form",
        clear_on_submit=True
    ):

        api_name = st.text_input(
            "API Name",
            placeholder="Example: JSONPlaceholder"
        )

        api_url = st.text_input(
            "API URL",
            placeholder="https://jsonplaceholder.typicode.com/posts/1"
        )

        add_api = st.form_submit_button(
            "Add API",
            type="primary",
            use_container_width=True
        )

    if add_api:

        if not api_name.strip() or not api_url.strip():

            st.error(
                "Please enter both API name and URL."
            )

        else:

            try:

                with st.spinner("Adding API..."):

                    response = httpx.post(
                        f"{BACKEND_URL}/monitor/add",
                        json={
                            "name": api_name.strip(),
                            "url": api_url.strip()
                        },
                        timeout=10
                    )

                if response.is_success:

                    st.success(
                        "API added to monitoring successfully!"
                    )

                    st.rerun()

                else:

                    try:
                        error_message = response.json().get(
                            "detail",
                            response.text
                        )
                    except ValueError:
                        error_message = response.text

                    st.error(
                        f"Could not add API: {error_message}"
                    )

            except httpx.RequestError as error:

                st.error(
                    f"Backend connection error: {error}"
                )

    st.divider()

    st.subheader("📋 Your Monitored APIs")

    if st.button("🔄 Refresh Monitoring List"):
        st.rerun()

    try:

        monitored_apis = get_monitored_apis()

        if monitored_apis:

            st.caption(
                f"Total APIs being monitored: {len(monitored_apis)}"
            )

            for api in monitored_apis:

                api_id = api["id"]
                name = api["name"]
                url = api["url"]

                with st.container(border=True):

                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:

                        st.markdown(f"### 🌐 {name}")

                        st.caption(url)

                        st.caption(
                            f"Monitoring ID: {api_id}"
                        )

                    with col2:

                        check_clicked = st.button(
                            "🔍 Check Status",
                            key=f"check_{api_id}",
                            use_container_width=True
                        )

                    with col3:

                        delete_clicked = st.button(
                            "🗑️ Delete",
                            key=f"delete_{api_id}",
                            use_container_width=True
                        )

                    if check_clicked:

                        try:

                            with st.spinner(
                                f"Checking {name}..."
                            ):

                                check_response = httpx.post(
                                    f"{BACKEND_URL}/monitor/check/{api_id}",
                                    timeout=15
                                )

                            if check_response.is_success:

                                check_data = check_response.json()

                                if check_data["status"] == "Online":
                                    st.success(
                                        f"🟢 {name} is ONLINE"
                                    )
                                else:
                                    st.error(
                                        f"🔴 {name} is OFFLINE"
                                    )

                                m1, m2, m3 = st.columns(3)

                                m1.metric(
                                    "Status",
                                    check_data["status"]
                                )

                                m2.metric(
                                    "HTTP Status Code",
                                    check_data["status_code"]
                                    if check_data["status_code"] is not None
                                    else "N/A"
                                )

                                m3.metric(
                                    "Response Time",
                                    f'{check_data["response_time_ms"]:.2f} ms'
                                )

                                st.caption(
                                    f'Last checked: {check_data["checked_at"]}'
                                )

                            else:

                                st.error(
                                    f"Monitoring check failed: {check_response.text}"
                                )

                        except httpx.RequestError as error:

                            st.error(
                                f"Could not check API: {error}"
                            )

                    if delete_clicked:

                        try:

                            delete_response = httpx.delete(
                                f"{BACKEND_URL}/monitor/delete/{api_id}",
                                timeout=10
                            )

                            if delete_response.is_success:

                                st.success(
                                    f"{name} removed from monitoring."
                                )

                                st.rerun()

                            else:

                                st.error(
                                    f"Could not delete API: {delete_response.text}"
                                )

                        except httpx.RequestError as error:

                            st.error(
                                f"Delete failed: {error}"
                            )

                    with st.expander(
                        f"📜 View History — {name}"
                    ):

                        try:

                            monitor_data = get_monitoring_history(
                                api_id
                            )

                            checks = monitor_data.get(
                                "history", []
                            )

                            total_checks = monitor_data.get(
                                "total_checks",
                                len(checks)
                            )

                            st.metric(
                                "Total Monitoring Checks",
                                total_checks
                            )

                            if checks:

                                history_df = pd.DataFrame(checks)

                                history_df["Status"] = history_df[
                                    "is_online"
                                ].map({
                                    1: "Online",
                                    0: "Offline",
                                    True: "Online",
                                    False: "Offline"
                                })

                                display_columns = [
                                    "id",
                                    "Status",
                                    "status_code",
                                    "response_time",
                                    "checked_at"
                                ]

                                st.dataframe(
                                    history_df[display_columns],
                                    use_container_width=True,
                                    hide_index=True
                                )

                                if len(history_df) > 1:

                                    chart_df = history_df.sort_values(
                                        "id"
                                    )

                                    fig = px.line(
                                        chart_df,
                                        x="checked_at",
                                        y="response_time",
                                        markers=True,
                                        title="Monitoring Response Time",
                                        labels={
                                            "checked_at": "Check Time",
                                            "response_time": "Response Time (ms)"
                                        }
                                    )

                                    fig = apply_light_chart(fig)

                                    st.plotly_chart(
                                        fig,
                                        use_container_width=True
                                    )

                            else:

                                st.info(
                                    "No monitoring checks yet. "
                                    "Click Check Status to begin."
                                )

                        except httpx.RequestError as error:

                            st.error(
                                f"Could not load monitoring history: {error}"
                            )

        else:

            st.info(
                "No APIs added yet. "
                "Use the form above to add your first API."
            )

    except httpx.RequestError as error:

        st.error(
            f"Could not load monitored APIs: {error}"
        )


# ==========================================
# ALERT HISTORY
# ==========================================

elif page == "Alert History":

    st.title("🚨 Alert History")

    st.caption(
        "Track API failures and recovery events."
    )

    st.divider()

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("🔄 Refresh Alerts"):
            st.rerun()

    try:

        alert_data = get_alert_history(limit=200)

        alerts = alert_data.get("alerts", [])

        total_alerts = alert_data.get(
            "total_alerts",
            len(alerts)
        )

        down_alerts = sum(
            1 for alert in alerts
            if alert.get("event_type") == "DOWN"
        )

        recovered_alerts = sum(
            1 for alert in alerts
            if alert.get("event_type") == "RECOVERED"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Alerts", total_alerts)
        c2.metric("🔴 DOWN Events", down_alerts)
        c3.metric("🟢 RECOVERED Events", recovered_alerts)

        st.divider()

        st.subheader("📋 Recorded Alerts")

        if alerts:

            filter_type = st.selectbox(
                "Filter Alerts",
                [
                    "All Alerts",
                    "DOWN",
                    "RECOVERED"
                ]
            )

            filtered_alerts = alerts

            if filter_type != "All Alerts":

                filtered_alerts = [
                    alert for alert in alerts
                    if alert.get("event_type") == filter_type
                ]

            if filtered_alerts:

                for alert in filtered_alerts:

                    event_type = alert.get(
                        "event_type",
                        "UNKNOWN"
                    )

                    api_name = alert.get(
                        "api_name",
                        "Unknown API"
                    )

                    with st.container(border=True):

                        col1, col2 = st.columns([3, 1])

                        with col1:

                            st.markdown(
                                f"### 🌐 {api_name}"
                            )

                            st.caption(
                                alert.get("api_url", "N/A")
                            )

                        with col2:

                            if event_type == "DOWN":
                                st.error("🔴 DOWN")

                            elif event_type == "RECOVERED":
                                st.success("🟢 RECOVERED")

                            else:
                                st.warning(event_type)

                        st.write(
                            alert.get(
                                "message",
                                "No message available."
                            )
                        )

                        a, b, c = st.columns(3)

                        a.metric(
                            "HTTP Status",
                            alert.get("status_code")
                            if alert.get("status_code") is not None
                            else "N/A"
                        )

                        response_time = alert.get("response_time")

                        b.metric(
                            "Response Time",
                            f"{response_time:.2f} ms"
                            if response_time is not None
                            else "N/A"
                        )

                        c.metric(
                            "Alert ID",
                            alert.get("id", "N/A")
                        )

                        st.caption(
                            f"Occurred at: {alert.get('created_at', 'N/A')}"
                        )

            else:

                st.info(
                    f"No {filter_type} events found."
                )

        else:

            st.success(
                "No alerts recorded. All monitored APIs are healthy "
                "or no failure/recovery events have occurred."
            )

    except httpx.RequestError as error:

        st.error(
            f"Could not load alert history: {error}"
        )

    except (KeyError, ValueError, TypeError) as error:

        st.error(
            f"Could not display alert data: {error}"
        )
