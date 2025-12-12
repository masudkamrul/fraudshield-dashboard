import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (
    run_fraudshield_scan,
    update_log,
    generate_pdf_report,
    get_example_website_table
)

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="FraudShield Dashboard",
    layout="wide",
    page_icon="🛡️"
)

# ---------------------------------------------------------
# PROFESSIONAL CLEAN CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    body {
        background-color: #f8f9fa;
    }

    .main-title {
        text-align: center;
        padding: 20px 0 10px 0;
    }

    .fs-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        margin-bottom: 25px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    /* URL Input Style */
    .stTextInput>div>div>input {
        font-size: 18px !important;
        padding: 14px 16px !important;
        height: 55px !important;
        border-radius: 8px !important;
        border: 1.5px solid #bdbdbd !important;
    }

    /* Risk badge */
    .risk-badge {
        padding: 10px 22px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 18px;
        display: inline-block;
        margin-bottom: 8px;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🛡️ FraudShield – Website Risk Evaluation</h1>", unsafe_allow_html=True)
st.write("A clean and professional dashboard demonstrating machine-learning–based website risk scoring.")


# ---------------------------------------------------------
# RISK CLASSIFICATION MATCHING EXTENSION POPUP
# ---------------------------------------------------------
def map_risk_style(risk_class, blacklist_flag=0):

    # Matches your Chrome extension color scheme and labels
    # (source: popup.js + popup.css)
    # Safe
    if blacklist_flag == 1:
        return "☠️ Blacklisted Threat", "#B71C1C"

    if risk_class == "Safe":
        return "🟢 Safe", "#4CAF50"

    if risk_class == "Low Risk":
        return "🟡 Low Risk", "#FFC107"

    if risk_class == "Suspicious":
        return "🟠 Suspicious", "#FF9800"

    if risk_class == "High Risk":
        return "🔴 High Risk", "#F44336"

    return "❓ Unknown", "#95a5a6"


# ---------------------------------------------------------
# SCANNER SECTION
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("🔍 Website Risk Scanner")

url = st.text_input("", placeholder="Enter website URL (e.g., https://example.com)")

scan_result = None

if st.button("Run Scan", use_container_width=True):

    with st.spinner("Analyzing website…"):
        scan_result = run_fraudshield_scan(url)

    if not scan_result:
        st.error("Unable to connect to FraudShield API.")
    else:
        risk_class = scan_result.get("risk_class", "Unknown")
        risk_score = float(scan_result.get("risk_score", 0))
        blacklist = scan_result.get("blacklist_flag", 0)

        display_label, badge_color = map_risk_style(risk_class, blacklist)

        # ---------------------------------------------------------
        # RESULT BLOCK (Compact + Professional)
        # ---------------------------------------------------------
        st.markdown("<div class='fs-card' style='text-align:center;'>", unsafe_allow_html=True)

        # Risk Badge
        st.markdown(
            f"""
            <div style="
                background:{badge_color};
                color:white;
                padding:10px 22px;
                border-radius:16px;
                display:inline-block;
                font-size:22px;
                font-weight:600;
                margin-bottom:10px;">
                {display_label}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Gauge Chart (pull closer)
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 40], "color": "#d4f6e4"},
                        {"range": [40, 70], "color": "#fff3cd"},
                        {"range": [70, 100], "color": "#f8d7da"}
                    ],
                },
                number={"font": {"size": 42}},
                title={"text": ""}
            )
        )

        st.plotly_chart(fig, use_container_width=False)

        # Summary
        st.markdown(
            f"""
            <p style="font-size:16px; margin-top:10px;">
            Website <strong>{url}</strong> is classified as <strong>{display_label}</strong><br>
            Risk Score: <strong>{risk_score:.1f}/100</strong>
            </p>
            """,
            unsafe_allow_html=True
        )

        update_log(st.session_state, url, risk_class)

        # PDF Report
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            "📄 Download PDF Report",
            pdf_bytes,
            "fraudshield_report.pdf",
            mime="application/pdf"
        )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# MODEL PERFORMANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("📊 Model Performance Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC Score", "0.805")
col3.metric("F1 Score", "0.91")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("🔬 Feature Importance Breakdown")

feature_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL", "Threat Match", "Keywords", "Hosting Risk"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07],
})
st.bar_chart(feature_data.set_index("Feature"))
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# EXAMPLE TABLE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("📝 Example Website Evaluations")
st.dataframe(get_example_website_table(), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SCAN HISTORY
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("📁 Recent Scan History")

if "history" in st.session_state:
    st.dataframe(pd.DataFrame(st.session_state["history"]), use_container_width=True)
else:
    st.write("No scans yet.")
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    "<p class='fs-footer'>FraudShield — Professional Real-Time Website Risk Evaluation</p>",
    unsafe_allow_html=True
)
