import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
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
# CUSTOM CSS (NEON + GLASSMORPHISM UI)
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* Global background */
    body {
        background: linear-gradient(135deg, #0f0f1a, #1b1b2f, #16213e);
        background-size: 300% 300%;
        animation: bg-animation 12s ease infinite;
    }

    @keyframes bg-animation {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Futuristic neon header */
    .fs-header {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(14px);
        padding: 30px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 0 18px #00eaff80;
        text-align: center;
        margin-bottom: 40px;
    }

    .fs-header h1 {
        color: #00eaff;
        text-shadow: 0 0 10px #00eaff;
    }

    /* Glassmorphism cards */
    .fs-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(16px);
        padding: 25px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 25px;
        box-shadow: 0 0 18px rgba(0,0,0,0.4);
        color: white;
    }

    /* Risk badges with neon glow */
    .risk-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 15px;
        margin-top: 10px;
        color: white;
        text-shadow: 0 0 10px white;
    }

    .risk-low { background-color: #2ecc71; box-shadow: 0 0 12px #2ecc71; }
    .risk-medium { background-color: #f1c40f; box-shadow: 0 0 12px #f1c40f; }
    .risk-high { background-color: #e74c3c; box-shadow: 0 0 12px #e74c3c; }

    /* Neon button */
    .stButton>button {
        background: linear-gradient(90deg, #00eaff, #006eff);
        color: black;
        font-weight: 700;
        border-radius: 10px;
        padding: 12px 20px;
        border: none;
        box-shadow: 0 0 12px #00eaff;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00bfff, 0 0 40px #0099ff;
        transform: scale(1.03);
    }

    h2, h3, h4 { color: #00eaff !important; }

    /* Footer */
    .fs-footer {
        text-align: center;
        margin-top: 40px;
        color: #ccc;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    """
    <div class="fs-header">
        <h1>🛡️ FraudShield Cyber Dashboard</h1>
        <p>AI-Powered Neon Security Interface · Real-Time Threat Evaluation</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# SCANNER (WITH ANIMATED RISK SCORE)
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔍 Real-Time Website Risk Scanner")

url = st.text_input("Enter URL to evaluate:", placeholder="https://example.com")
scan_result = None

if st.button("Run Scan", use_container_width=True):
    with st.spinner("Deploying analysis modules…"):
        scan_result = run_fraudshield_scan(url)

    if not scan_result:
        st.error("Unable to connect to API.")
    else:
        risk_class = scan_result.get("risk_class", "Unknown")
        risk_score = float(scan_result.get("risk_score", 0))

        badge_class = (
            "risk-low" if risk_class=="Legitimate" else
            "risk-medium" if risk_class=="Suspicious" else
            "risk-high"
        )
        st.markdown(f"<span class='risk-badge {badge_class}'>{risk_class}</span>", unsafe_allow_html=True)

        # ANIMATED RISK VALUE
        placeholder = st.empty()
        for i in range(0, int(risk_score)+1):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=i,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#00eaff"},
                    "steps": [
                        {"range": [0, 40], "color": "#2ecc71"},
                        {"range": [40, 70], "color": "#f1c40f"},
                        {"range": [70, 100], "color": "#e74c3c"}
                    ]
                }
            ))
            placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.015)

        # Log scan
        update_log(st.session_state, url, risk_class)

        # Report Download
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            "📄 Download PDF Report",
            pdf_bytes,
            "fraudshield_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODEL PERFORMANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("📊 Model Performance Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC", "0.805")
col3.metric("F1 Score", "0.91")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔬 Feature Importance Analysis")

feature_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL", "Threat Match", "Keywords", "Hosting Risk"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07],
})

st.bar_chart(feature_data.set_index("Feature"))

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# EXAMPLE SITES
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("📝 Example Websites Evaluation Table")

st.dataframe(get_example_website_table(), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("📁 Scan History")

if "history" in st.session_state:
    st.dataframe(pd.DataFrame(st.session_state["history"]), use_container_width=True)
else:
    st.write("No scans yet.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    "<p class='fs-footer'>© FraudShield — Neon Cybersecurity Interface</p>",
    unsafe_allow_html=True
)
