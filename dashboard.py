import streamlit as st
import requests
import pandas as pd
import time

# -------------------------------------------
# CONFIG
# -------------------------------------------
st.set_page_config(
    page_title="FraudShield – Website Risk Evaluation Dashboard",
    layout="centered"
)

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"

st.title("🔎 FraudShield – Website Risk Evaluation Dashboard")
st.write(
    "Evaluate online shopping websites in real-time using "
    "**FraudShield’s machine-learning risk analysis system.**"
)

# -------------------------------------------
# URL SCANNER
# -------------------------------------------
st.header("🔵 1. Website Risk Scanner")

url = st.text_input("Enter website URL", placeholder="https://example.com")

if st.button("Check Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Analyzing website…"):
            try:
                response = requests.post(API_URL, json={"url": url}, timeout=10)
                data = response.json()
            except Exception as e:
                st.error("Could not connect to FraudShield API.")
                st.stop()

        risk_class = data.get("risk_class", "Unknown")
        risk_score = float(data.get("risk_score", 0))
        blacklist_flag = data.get("blacklist_flag", 0)

        # Output color scheme
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
            <div style="padding:15px;border-radius:12px;background-color:{color};
            color:white;text-align:center;font-size:18px;">
                <strong>{risk_class}</strong><br>
                Risk Score: {risk_score:.2f}%
            </div>
            """,
            unsafe_allow_html=True
        )

        if blacklist_flag:
            st.error("⚠ This website is flagged as **Blacklisted / Known Threat**.")

        # Save to activity log
        if "log" not in st.session_state:
            st.session_state["log"] = []
        st.session_state["log"].append(
            {"time": time.strftime("%H:%M:%S"), "url": url, "result": risk_class}
        )

# -------------------------------------------
# EXAMPLE EVALUATIONS
# -------------------------------------------
st.header("🟣 2. Example Website Evaluations")

example_data = pd.DataFrame([
    ["amazon.com", "Safe"],
    ["ebay.com", "Low Risk"],
    ["cheapshop247.net", "High Risk"],
    ["brand-outlet-deals.biz", "Suspicious"],
    ["newtechstore.xyz", "High Risk"],
], columns=["Website", "Risk Result"])

st.table(example_data)

# -------------------------------------------
# MODEL PERFORMANCE
# -------------------------------------------
st.header("🟡 3. Model Performance Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Accuracy", "95%")

with col2:
    st.metric("AUC Score", "0.805")

with col3:
    st.metric("F1 Score", "0.91")

st.write(
    "FraudShield’s model performance metrics reflect strong ability to distinguish "
    "legitimate websites from deceptive or fraudulent environments."
)

# -------------------------------------------
# FEATURE IMPORTANCE CHART
# -------------------------------------------
st.header("🟠 4. Feature Importance")

feature_data = pd.DataFrame({
    "Feature": [
        "Domain Age", "SSL Security", "Threatlist Match",
        "Suspicious Keywords", "Hosting Risk Signals"
    ],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07]
})

st.bar_chart(feature_data.set_index("Feature"))

# -------------------------------------------
# BACKEND ACTIVITY LOG
# -------------------------------------------
st.header("🟤 5. Recent Evaluation Log")

if "log" in st.session_state and len(st.session_state["log"]) > 0:
    st.table(pd.DataFrame(st.session_state["log"]))
else:
    st.write("No recent activity recorded.")

# -------------------------------------------
# HOW FRAUDSHIELD WORKS
# -------------------------------------------
st.header("🟢 6. How FraudShield Works")

st.write("""
FraudShield evaluates websites by analyzing a combination of safety indicators such as:

- Domain legitimacy and age  
- SSL and connection security  
- Threat intelligence signals  
- Website behavior patterns  
- Metadata consistency  
- Risk signatures historically linked to fraudulent websites  

The backend model generates a **risk score** and a **classification**, which are returned instantly through the API.
""")

st.info("FraudShield is designed to support consumers and businesses by identifying "
        "potential scam websites before financial harm occurs.")
