import streamlit as st

st.set_page_config(page_title="FraudShield Dashboard", layout="wide")

st.markdown("""
# 🛡️ FraudShield – AI-Driven Risk Evaluation Platform
Welcome to the FraudShield dashboard.  
This platform demonstrates the capabilities of our machine-learning system
that detects fraudulent and deceptive online shopping environments in real time.
""")

st.markdown("---")

st.subheader("📌 Platform Overview")

st.write("""
FraudShield provides:

- Real-time website fraud detection  
- ML-powered risk scoring  
- Domain security analysis  
- Threat intelligence signals  
- PDF reporting engine  
- API access for business integration  
""")

st.info("Use the sidebar to navigate through FraudShield’s features.")
