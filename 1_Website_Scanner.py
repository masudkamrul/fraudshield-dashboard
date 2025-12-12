import streamlit as st
import plotly.graph_objects as go
from utils import run_fraudshield_scan, update_log, generate_pdf_report

st.title("🔍 Website Risk Scanner")

url = st.text_input("Enter website URL", placeholder="https://example.com")

if st.button("Run Scan"):
    with st.spinner("Analyzing website…"):
        data = run_fraudshield_scan(url)

    if not data:
        st.error("API unreachable. Please try again.")
    else:
        risk_class = data.get("risk_class", "Unknown")
        risk_score = float(data.get("risk_score", 0))
        blacklist = data.get("blacklist_flag", 0)

        # Risk gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "black"},
                "steps": [
                    {"range": [0, 40], "color": "green"},
                    {"range": [40, 70], "color": "yellow"},
                    {"range": [70, 100], "color": "red"}
                ]
            },
            title={"text": f"Risk Score – {risk_class}"}
        ))

        st.plotly_chart(fig, use_container_width=True)

        # Log history
        update_log(st.session_state, url, risk_class)

        # PDF report
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf"
        )
