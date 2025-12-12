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
# CUSTOM CSS (BEAUTIFUL COLORFUL UI)
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* Main container width */
    .main {
        padding: 0rem 2rem;
    }

    /* Gradient header styling */
    .fs-header {
        background: linear-gradient(90deg, #4b6cb7, #182848);
        padding: 35px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 35px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }

    /* Card-style sections */
    .fs-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 14px;
        margin-bottom: 25px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    }

    /* Risk badge styling */
    .risk-badge {
        display: inline-block;
        padding: 6px 18px;
        font-weight: 600;
        border-radius: 25px;
        color: white;
        margin-top: 10px;
    }

    .risk-low { background-color: #2ecc71; }
    .risk-medium { background-color: #f1c40f; }
    .risk-high { background-color: #e74c3c; }

    /* Footer */
    .fs-footer {
        text-align:center;
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
st.markdown(
    """
    <div class="fs-header">
        <h1>🛡️ FraudShield – Website Risk Evaluation Dashboard</h1>
        <p style="font-size:18px;">AI-powered real-time detection of fraudulent or deceptive online environments</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# SCANNER CARD
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔍 Website Risk Scanner")

url = st.text_input("Enter website URL", placeholder="https://example.com")

scan_result = None

if st.button("Run Scan", use_container_width=True):
    with st.spinner("Analyzing website…"):
        scan_result = run_fraudshield_scan(url)

    if not scan_result:
        st.error("Unable to connect to FraudShield API.")
    else:
        risk_class = scan_result.get("risk_class", "Unknown")
        risk_score = float(scan_result.get("risk_score", 0))

        # Risk badge
        badge_class = "risk-low" if risk_class=="Legitimate" else "risk-medium" if risk_class=="Suspicious" else "risk-high"
        st.markdown(f"<span class='risk-badge {badge_class}'>{risk_class}</span>", unsafe_allow_html=True)

        # Gauge chart
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 40], "color": "#2ecc71"},
                        {"range": [40, 70], "color": "#f1c40f"},
                        {"range": [70, 100], "color": "#e74c3c"},
                    ],
                },
                title={"text": f"Risk Score"}
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Activity Log
        update_log(st.session_state, url, risk_class)

        # PDF Download
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODEL PERFORMANCE CARD
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("📊 Model Performance Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%", "+0.2%")
col2.metric("AUC Score", "0.805", "+0.01")
col3.metric("F1 Score", "0.91", "+0.03")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FEATURE IMPORTANCE CARD
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔬 Feature Importance Breakdown")

feature_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL Security", "Threatlist Match", "Suspicious Keywords", "Hosting Risk"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07],
})

st.bar_chart(feature_data.set_index("Feature"))

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# EXAMPLE WEBSITES
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("📝 Example Website Evaluations")

example_df = get_example_website_table()
st.dataframe(example_df, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# RECENT HISTORY
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("📁 Recent Scan History")

if "history" in st.session_state and len(st.session_state["history"]) > 0:
    st.dataframe(pd.DataFrame(st.session_state["history"]), use_container_width=True)
else:
    st.write("No scans performed yet.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    "<p class='fs-footer'>FraudShield — Real-time fraud detection for safer online interactions.</p>",
    unsafe_allow_html=True
)
