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
# CORPORATE CLEAN CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    body {
        background-color: #f5f6f8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .main-title {
        text-align: center;
        padding: 20px 0 5px 0;
    }

    .subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 15px;
    }

    .fs-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #e2e6ea;
        margin-bottom: 22px;
        box-shadow: 0 2px 5px rgba(15,23,42,0.03);
    }

    /* Section header bars */
    .section-header {
        padding: 10px 16px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        margin-bottom: 14px;
        font-size: 18px;
    }
    .section-blue { background: #2563eb; }
    .section-purple { background: #6d28d9; }
    .section-orange { background: #ea580c; }
    .section-green { background: #16a34a; }
    .section-red { background: #b91c1c; }
    .section-grey { background: #4b5563; }

    /* Scanner Input Bar (Sucuri-style) */
    .scan-wrapper {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-top: 18px;
        margin-bottom: 20px;
    }
    .scan-bar {
        width: 92%;
        max-width: 900px;
        display: flex;
        align-items: center;
        border: 2px solid #00897B;
        border-radius: 6px;
        overflow: hidden;
        background: white;
    }
    .scan-input {
        flex: 1;
        padding: 14px 16px;
        font-size: 18px;
        border: none !important;
        outline: none !important;
        color: #333;
    }
    .scan-input::placeholder {
        color: #999;
    }
    .scan-btn {
        background-color: #00897B;
        color: white;
        padding: 14px 28px;
        font-size: 18px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }
    .scan-btn:hover {
        background-color: #006F63;
    }

    .info-box {
        background: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 14px;
        color: #374151;
        margin-top: 8px;
    }

    .fs-footer {
        text-align: center;
        color: gray;
        font-size: 13px;
        margin-top: 40px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🛡️ FraudShield – Website Risk Evaluation Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Professional interface to demonstrate how FraudShield evaluates website safety using machine learning and security signals.</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# RISK CLASS → LABEL + COLOR
# ---------------------------------------------------------
def map_risk_style(risk_class: str, blacklist_flag: int = 0):
    if blacklist_flag:
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
# TABS
# ---------------------------------------------------------
tab_scanner, tab_model, tab_api, tab_threats, tab_arch, tab_logic = st.tabs(
    [
        "Scanner",
        "Model Intelligence",
        "API Explorer",
        "Threat Categories",
        "Architecture",
        "Risk Scoring Logic",
    ]
)

# =========================================================
# 1️⃣ SCANNER TAB
# =========================================================
with tab_scanner:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-blue'>🔍 Website Risk Scanner</div>", unsafe_allow_html=True)

    st.write("Enter any website URL below to see its FraudShield risk classification and score.")

    # ---------------------- NEW SCANNER BOX ----------------------
    st.markdown('<div class="scan-wrapper">', unsafe_allow_html=True)
    col_input, col_button = st.columns([6, 1])

    with col_input:
        url = st.text_input(
            "",
            placeholder="example.com",
            key="scanner_url",
            label_visibility="collapsed"
        )

    with col_button:
        scan_clicked = st.button("Scan Website", key="scan_button")

    st.markdown('</div>', unsafe_allow_html=True)
    # --------------------------------------------------------------

    st.markdown(
        """
        <div class="info-box">
        Tip: This scanner uses the same backend engine as the FraudShield browser extension and API.
        </div>
        """,
        unsafe_allow_html=True
    )

    scan_result = None

    if scan_clicked:
        if not url.strip():
            st.error("Please provide a valid URL before scanning.")
        else:
            with st.spinner("Analyzing website…"):
                scan_result = run_fraudshield_scan(url)

            if not scan_result:
                st.error("Unable to connect to FraudShield API.")
            else:
                risk_class = scan_result.get("risk_class", "Unknown")
                risk_score = float(scan_result.get("risk_score", 0))
                blacklist_flag = scan_result.get("blacklist_flag", 0)

                display_label, badge_color = map_risk_style(risk_class, blacklist_flag)

                st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

                # Risk Badge
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-bottom:10px;">
                        <span style="
                            background:{badge_color};
                            color:white;
                            padding:10px 26px;
                            border-radius:18px;
                            font-size:22px;
                            font-weight:600;">
                            {display_label}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Gauge Chart
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
                                {"range": [70, 100], "color": "#f8d7da"},
                            ],
                        },
                        number={"font": {"size": 40}},
                    )
                )
                st.plotly_chart(fig, use_container_width=False)

                st.markdown(
                    f"""
                    **Summary**

                    - Website: **{url}**  
                    - Classification: **{display_label}**  
                    - Risk Score: **{risk_score:.1f} / 100**  
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    """
                    **Key signals used in this evaluation include:**
                    - Domain age and trust history  
                    - HTTPS / SSL configuration  
                    - Security headers (HSTS, CSP)  
                    - Google Safe Browsing blacklist  
                    - Mixed-content flags  
                    """
                )

                update_log(st.session_state, url, risk_class)

                pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
                st.download_button(
                    "📄 Download PDF Report",
                    pdf_bytes,
                    "fraudshield_report.pdf",
                    mime="application/pdf",
                )

                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------- (REMAINING TABS LEFT UNCHANGED) ---------------------
# Your Model Intelligence, API Explorer, Threat Categories, Architecture,
# and Risk Logic tabs remain EXACTLY the same as the original file.
# --------------------------------------------------------------------------

st.markdown(
    "<p class='fs-footer'>FraudShield — Professional Real-Time Website Risk Evaluation</p>",
    unsafe_allow_html=True,
)
