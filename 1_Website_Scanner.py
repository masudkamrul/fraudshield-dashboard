import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
import time

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"

st.title("🔍 Website Risk Scanner")

url = st.text_input("Enter a website URL", placeholder="https://example.com")

scan_data = None

if st.button("Run Scan"):
    with st.spinner("Evaluating website…"):
        response = requests.post(API_URL, json={"url": url}).json()
        scan_data = response

if scan_data:
    risk_class = scan_data["risk_class"]
    risk_score = float(scan_data["risk_score"])
    blacklist = scan_data.get("blacklist_flag", 0)

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "red"},
            "steps": [
                {"range": [0, 40], "color": "green"},
                {"range": [40, 70], "color": "yellow"},
                {"range": [70, 100], "color": "red"},
            ],
        },
        title={"text": f"Risk Score – {risk_class}"}
    ))

    st.plotly_chart(fig)

    st.subheader("Indicators Identified")
    st.write("""
    - Domain Age Check  
    - SSL Certificate Validation  
    - Threat List Lookup  
    - Metadata Structure  
    - Hosting Patterns  
    """)

    # Add PDF report button
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FraudShield Risk Report", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Website: {url}", ln=True)
        pdf.cell(0, 10, f"Risk Class: {risk_class}", ln=True)
        pdf.cell(0, 10, f"Risk Score: {risk_score}", ln=True)
        return pdf.output(dest="S").encode("latin-1")

    st.download_button(
        label="📄 Download PDF Report",
        data=generate_pdf(),
        file_name="fraudshield_report.pdf",
        mime="application/pdf"
    )
