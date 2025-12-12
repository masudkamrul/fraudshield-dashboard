import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(
    page_title="FraudShield – Website Risk Evaluation",
    layout="centered"
)

st.title("🔎 FraudShield – Website Risk Evaluation")
st.write("Enter any website URL to evaluate its safety using FraudShield’s machine learning model.")

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"

url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Check Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Analyzing website…"):
            try:
                response = requests.post(API_URL, json={"url": url}, timeout=10)
                data = response.json()
            except:
                st.error("Could not connect to FraudShield API.")
                st.stop()

        risk_class = data.get("risk_class", "Unknown")
        risk_score = float(data.get("risk_score", 0))
        blacklist_flag = data.get("blacklist_flag", 0)

        # Color scheme
        color = "#4CAF50"
        if risk_class == "Low Risk":
            color = "#FFC107"
        elif risk_class == "Suspicious":
            color = "#FF9800"
        elif risk_class == "High Risk":
            color = "#F44336"
        if blacklist_flag == 1:
            color = "#B71C1C"

        st.markdown(
            f"""
            <div style="padding:15px;border-radius:12px;background-color:{color};color:white;text-align:center;">
                <h3>{risk_class}</h3>
                <p><strong>Risk Score:</strong> {risk_score:.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if blacklist_flag:
            st.error("⚠ This website is flagged as a known threat.")

        # Activity log
        if "log" not in st.session_state:
            st.session_state["log"] = []
        st.session_state["log"].append(
            {"time": time.strftime("%H:%M:%S"), "url": url, "result": risk_class}
        )

st.subheader("🟤 Recent Checks")
if "log" in st.session_state and len(st.session_state["log"]) > 0:
    st.table(pd.DataFrame(st.session_state["log"]))
else:
    st.write("No scans yet.")
