import streamlit as st
import requests
import json

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"

st.title("🔌 API Explorer")

url = st.text_input("Test API with URL")

if st.button("Send Request"):
    response = requests.post(API_URL, json={"url": url})
    st.json(response.json())

st.markdown("### Code Examples:")
st.code("""
import requests
requests.post("API_URL", json={"url": "example.com"}).json()
""")
