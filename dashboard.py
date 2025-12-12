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
    layout="wide"
)

# Optional logo at top
st.markdown(
    """
    <div style="text-align:center;">
        <img src="https://i.imgur.com/wQK3O0M.png" width="140">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ FraudShield – Website Risk Evaluation Dashboard")
st.write("Evaluate a website’s fraud risk using real-time machine learning scoring.")


# ---------------------------------------------------------
# 1️⃣ WEBSITE SCANNING SECTION
# ---------------------------------------------------------
st.header("🔍 Website Risk Scanner")

col_input, col_button = st.columns([3, 1])

with col_input:
    url = st.text_input("Enter URL to scan", placeholder="https://example.com")

with col_button:
    run_scan = st.button("Scan")

scan_response = None

if run_scan:
    if not url:
        st.warning("Please enter a valid website URL.")
    else:
        with st.spinner("Analyzing website…"):
            scan_response = run_fraudshield_scan(url)

    if scan_response is None:
        st.error("Could not connect to the FraudShield API.")
    else:
        risk_class = scan_response.get("risk_class", "Unknown")
        risk_score = float(scan_response.get("risk_score", 0))
        blacklist_flag = scan_response.get("blacklist_flag", 0)

        # -------------------------------------------
        #  Gauge Visualization
        # -------------------------------------------
        st.subheader("Risk Score Overview")

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "green"},
                        {"range": [40, 70], "color": "yellow"},
                        {"range": [70, 100], "color": "red"}
                    ],
                    "bar": {"color": "black"},
                },
                title={"text": f"Risk Level: {risk_class}"}
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Update session log
        update_log(st.session_state, url, risk_class)

        # -------------------------------------------
        #  PDF REPORT DOWNLOAD
        # -------------------------------------------
        st.subheader("📄 Download FraudShield Report")

        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)

        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf"
        )

        # -------------------------------------------
        #  BLACKLIST WARNING
        # -------------------------------------------
        if blacklist_flag == 1:
            st.error("⚠ This website is listed on known threat/blacklist sources.")


# ---------------------------------------------------------
# 2️⃣ EXAMPLE WEBSITE EVALUATIONS
# ---------------------------------------------------------
st.header("🟣 Example Website Evaluations")

example_df = get_example_website_table()
st.table(example_df)


# ---------------------------------------------------------
# 3️⃣ MODEL PERFORMANCE SECTION
# ---------------------------------------------------------
st.header("🟡 Model Performance Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC Score", "0.805")
col3.metric("F1 Score", "0.91")

st.write(
    "These metrics reflect FraudShield’s ability to distinguish legitimate websites from deceptive ones."
)


# ---------------------------------------------------------
# 4️⃣ FEATURE IMPORTANCE (STATIC DEMO)
# ---------------------------------------------------------
st.header("🟠 Feature Importance")

feature_df = pd.DataFrame({
    "Feature": ["Domain Age", "SSL Validity", "Threatlist Match", "Keyword Patterns", "Hosting Signals"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07]
})

st.bar_chart(feature_df.set_index("Feature"))


# ---------------------------------------------------------
# 5️⃣ ACTIVITY LOG
# ---------------------------------------------------------
st.header("🟤 Recent Scans (Activity Log)")

if "history" in st.session_state and len(st.session_state["history"]) > 0:
    st.dataframe(pd.DataFrame(st.session_state["history"]))
else:
    st.write("No scans recorded yet.")


# ---------------------------------------------------------
# 6️⃣ HOW FRAUDSHIELD WORKS
# ---------------------------------------------------------
st.header("🧠 How FraudShield Works")

st.write("""
FraudShield evaluates websites using a combination of domain intelligence, 
security indicators, threat intelligence, metadata signals, and machine learning scoring.  
The output is a **risk score** and **classification** that help users make safer decisions.
""")
