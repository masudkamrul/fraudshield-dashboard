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
st.set_page_config(page_title="FraudShield Dashboard", layout="wide")

st.title("🛡️ FraudShield – Website Risk Evaluation Dashboard")
st.write(
    "Evaluate online shopping websites using FraudShield’s machine-learning risk scoring system."
)

# ---------------------------------------------------------
# SCANNER SECTION
# ---------------------------------------------------------
st.header("🔍 Website Risk Scanner")

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

        # Gauge chart
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 40], "color": "green"},
                        {"range": [40, 70], "color": "yellow"},
                        {"range": [70, 100], "color": "red"},
                    ],
                },
                title={"text": f"Risk Level: {risk_class}"}
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Activity log
        update_log(st.session_state, url, risk_class)

        # PDF report
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf"
        )

# ---------------------------------------------------------
# MODEL PERFORMANCE
# ---------------------------------------------------------
st.header("📊 Model Performance")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC Score", "0.805")
col3.metric("F1 Score", "0.91")

# ---------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------
st.header("🔬 Feature Importance (Key Signals)")

feature_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL Security", "Threatlist Match", "Suspicious Keywords", "Hosting Risk"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07],
})

st.bar_chart(feature_data.set_index("Feature"))

# ---------------------------------------------------------
# EXAMPLE WEBSITES TABLE
# ---------------------------------------------------------
st.header("📝 Example Results")

example_df = get_example_website_table()
st.table(example_df)

# ---------------------------------------------------------
# LOG HISTORY
# ---------------------------------------------------------
st.header("📁 Recent Scan History")

if "history" in st.session_state and len(st.session_state["history"]) > 0:
    st.dataframe(pd.DataFrame(st.session_state["history"]))
else:
    st.write("No scans performed yet.")

# ---------------------------------------------------------
# DESCRIPTION
# ---------------------------------------------------------
st.header("ℹ️ How FraudShield Works")

st.write(
    """
FraudShield evaluates websites using multiple signals:

• Domain trust and age  
• SSL configuration  
• Threat intelligence sources  
• Website metadata consistency  
• Risk patterns common in fraudulent sites  

These are combined into a machine-learning risk score and classification.
"""
)
