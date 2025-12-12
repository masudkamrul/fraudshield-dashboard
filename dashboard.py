import streamlit as st
import requests
import pandas as pd
import time
from fpdf import FPDF

# -----------------------------------------------------
# PAGE CONFIG (Theme + Title)
# -----------------------------------------------------
st.set_page_config(
    page_title="FraudShield – Risk Evaluation Dashboard",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional theme
st.markdown("""
<style>
    .main {background-color: #F5F7FA;}
    .title {color: #0A3D62; font-weight:700; font-size:36px; text-align:center;}
    .subtitle {color: #3C6382; font-size:18px; text-align:center;}
    .section-header {color:#0A3D62; font-size:26px; margin-top:25px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# TOP LOGO + TITLE
# -----------------------------------------------------

# (If you ever get a real logo file, we can add it. For now we simulate a logo)

st.markdown("<p class='title'>🛡️ FraudShield Risk Evaluation Dashboard</p>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Machine-learning system for real-time website safety analysis</p>", unsafe_allow_html=True)

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"   # ← YOUR API


# -----------------------------------------------------
# 1️⃣ URL SCANNER
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🔵 1. Website Risk Scanner</h3>", unsafe_allow_html=True)

url = st.text_input("Enter website URL", placeholder="https://example.com")

scan_result = None  # store for PDF generation

if st.button("Check Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Analyzing website…"):
            try:
                response = requests.post(API_URL, json={"url": url}, timeout=10)
                data = response.json()
                scan_result = data
            except Exception as e:
                st.error("Could not connect to FraudShield API.")
                st.stop()

        risk_class = data.get("risk_class", "Unknown")
        risk_score = float(data.get("risk_score", 0))
        blacklist_flag = data.get("blacklist_flag", 0)

        # Output color selection
        color = "#4CAF50"  # default safe
        if risk_class == "Low Risk": color = "#FFC107"
        elif risk_class == "Suspicious": color = "#FF9800"
        elif risk_class == "High Risk": color = "#F44336"
        if blacklist_flag: color = "#B71C1C"

        # Display card
        st.markdown(
            f"""
            <div style="padding:15px;border-radius:12px;background-color:{color};
            color:white;text-align:center;font-size:20px;">
                <strong>{risk_class}</strong><br>
                Risk Score: {risk_score:.2f}%
            </div>
            """,
            unsafe_allow_html=True
        )

        if blacklist_flag:
            st.error("⚠️ This website is flagged as a **Blacklisted Threat**.")

        # Save activity log
        if "log" not in st.session_state:
            st.session_state["log"] = []
        st.session_state["log"].append(
            {"time": time.strftime("%H:%M:%S"), "url": url, "result": risk_class}
        )


# -----------------------------------------------------
# 2️⃣ EXAMPLE EVALUATIONS
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🟣 2. Example Website Evaluations</h3>", unsafe_allow_html=True)

sample_data = pd.DataFrame([
    ["amazon.com", "Safe"],
    ["ebay.com", "Low Risk"],
    ["cheapshop247.net", "High Risk"],
    ["brand-outlet-deals.biz", "Suspicious"],
    ["newtechstore.xyz", "High Risk"],
], columns=["Website", "Classification"])

st.table(sample_data)


# -----------------------------------------------------
# 3️⃣ MODEL PERFORMANCE
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🟡 3. Model Performance Overview</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC", "0.805")
col3.metric("F1 Score", "0.91")


# -----------------------------------------------------
# 4️⃣ FEATURE IMPORTANCE
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🟠 4. Feature Importance</h3>", unsafe_allow_html=True)

feat_data = pd.DataFrame({
    "Feature": ["Domain Age", "SSL Security", "Threatlist Match", "Suspicious Keywords", "Hosting Signals"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07]
})
st.bar_chart(feat_data.set_index("Feature"))


# -----------------------------------------------------
# 5️⃣ BACKEND ACTIVITY LOG
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🟤 5. Recent Activity Log</h3>", unsafe_allow_html=True)

if "log" in st.session_state and len(st.session_state["log"]) > 0:
    st.table(pd.DataFrame(st.session_state["log"]))
else:
    st.info("No recent evaluations recorded.")


# -----------------------------------------------------
# 6️⃣ HOW FRAUDSHIELD WORKS
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>🟢 6. How FraudShield Works</h3>", unsafe_allow_html=True)

st.write("""
FraudShield analyzes multiple website signals including:

- Domain age & registration trust  
- SSL security & HTTPS integrity  
- Known threatlist matches  
- Hosting risk indicators  
- Keyword-based scam signatures  
- Behavioral and metadata consistency  

The backend model converts these into a **risk score** and **risk classification**, delivered instantly through the API.
""")


# -----------------------------------------------------
# 7️⃣ DOWNLOAD RISK REPORT (PDF)
# -----------------------------------------------------
st.markdown("<h3 class='section-header'>📄 7. Download Website Report (PDF)</h3>", unsafe_allow_html=True)

def generate_pdf(url, result):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FraudShield Risk Report", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Website: {url}", ln=True)
    pdf.cell(0, 10, f"Risk Class: {result.get('risk_class')}", ln=True)
    pdf.cell(0, 10, f"Risk Score: {result.get('risk_score')}%", ln=True)
    pdf.cell(0, 10, f"Blacklisted: {result.get('blacklist_flag')}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 8, "This automated report was generated using the FraudShield ML model.")

    return pdf.output(dest="S").encode("latin-1")

if scan_result:
    pdf_data = generate_pdf(url, scan_result)
    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_data,
        file_name="fraudshield_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("Run a scan first to download a report.")
