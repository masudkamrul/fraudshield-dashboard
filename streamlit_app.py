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
# CLEAN PROFESSIONAL CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* White background */
    body {
        background-color: #f8f9fa;
    }

    /* Title spacing */
    .main-title {
        text-align: center;
        padding: 20px 0 10px 0;
    }

    /* Clean card style */
    .fs-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        margin-bottom: 25px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    /* Risk badges */
    .risk-badge {
        padding: 6px 14px;
        border-radius: 14px;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
        color: white;
        font-size: 13.5px;
    }

    .risk-low    { background-color: #2ecc71; }
    .risk-medium { background-color: #f1c40f; }
    .risk-high   { background-color: #e74c3c; }

    /* Footer */
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
st.markdown("<h1 class='main-title'>🛡️ FraudShield – Website Risk Evaluation</h1>", unsafe_allow_html=True)
st.write(
    "A clean and simple dashboard to demonstrate how FraudShield evaluates online shopping websites for risk."
)

# ---------------------------------------------------------
# SCANNER (Professional Look)
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔍 Website Risk Scanner")

url = st.text_input("Enter website URL", placeholder="https://example.com")
scan_result = None

if st.button("Run Scan"):
    with st.spinner("Analyzing website…"):
        scan_result = run_fraudshield_scan(url)

    if not scan_result:
        st.error("Unable to connect to FraudShield API.")
    else:
        risk_class = scan_result.get("risk_class", "Unknown")
        risk_score = float(scan_result.get("risk_score", 0))

        # Badge color
        badge = (
            "risk-low" if risk_class == "Legitimate" else
            "risk-medium" if risk_class == "Suspicious" else
            "risk-high"
        )
        st.markdown(f"<span class='risk-badge {badge}'>{risk_class}</span>", unsafe_allow_html=True)

        # Gauge chart
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
                title={"text": "Risk Score"}
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Log
        update_log(st.session_state, url, risk_class)

        # Report
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf"
        )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODEL PERFORMANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
st.subheader("📊 Model Performance")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC Score", "0.805")
col3.metric("F1 Score", "0.91")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔬 Feature Importance")

feature_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL Security", "Threatlist Match", "Keywords", "Hosting Risk"],
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
st.markdown("<p class='fs-footer'>FraudShield — Professional, Real-Time Fraud Detection</p>", unsafe_allow_html=True)
