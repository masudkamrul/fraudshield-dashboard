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
# PROFESSIONAL CLEAN CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    body {
        background-color: #f8f9fa;
    }

    .main-title {
        text-align: center;
        padding: 20px 0 10px 0;
    }

    .fs-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        margin-bottom: 25px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    /* URL Input Style */
    .stTextInput>div>div>input {
        font-size: 18px !important;
        padding: 14px 16px !important;
        height: 55px !important;
        border-radius: 8px !important;
        border: 1.5px solid #bdbdbd !important;
    }

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
    "A professional dashboard demonstrating how FraudShield evaluates online shopping websites using machine-learning and security signals."
)

# ---------------------------------------------------------
# RISK CLASS → LABEL + COLOR (MATCHES EXTENSION)
# ---------------------------------------------------------
def map_risk_style(risk_class: str, blacklist_flag: int = 0):
    """
    Map backend risk_class + blacklist flag to the same
    labels & colors used in the Chrome extension.
    """

    if blacklist_flag:
        return "☠️ Blacklisted Threat", "#B71C1C"

    if risk_class == "Safe":
        return "🟢 Safe", "#4CAF50"

    if risk_class == "Low Risk":
        return "🟡 Low Risk", "#FFC107"

    if risk_class == "Suspicious":
        return "🟠 Suspicious", "#FF9800"

    if risk_class == "High Risk":
        return "🔴 High Risk", "#F44336"

    return "❓ Unknown", "#95a5a6"


# ---------------------------------------------------------
# TABS FOR 1–6 SECTIONS
# ---------------------------------------------------------
tab_scanner, tab_model, tab_api, tab_threats, tab_arch, tab_logic = st.tabs(
    [
        "Scanner",
        "Model Intelligence",
        "API Explorer",
        "Threat Categories",
        "Architecture",
        "Risk Scoring Logic",
    ]
)

# =========================================================
# 1️⃣ SCANNER TAB
# =========================================================
with tab_scanner:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("🔍 Website Risk Scanner")

    url = st.text_input(
        "",
        placeholder="Enter website URL (e.g., https://example.com)",
        key="scanner_url",
    )

    scan_result = None

    if st.button("Run Scan", use_container_width=True, key="scan_button"):
        with st.spinner("Analyzing website…"):
            scan_result = run_fraudshield_scan(url)

        if not scan_result:
            st.error("Unable to connect to FraudShield API.")
        else:
            risk_class = scan_result.get("risk_class", "Unknown")
            risk_score = float(scan_result.get("risk_score", 0))
            blacklist_flag = scan_result.get("blacklist_flag", 0)

            display_label, badge_color = map_risk_style(risk_class, blacklist_flag)

            # Result card (badge + gauge together)
            st.markdown("<div class='fs-card' style='text-align:center;'>", unsafe_allow_html=True)

            # Risk badge
            st.markdown(
                f"""
                <div style="
                    background:{badge_color};
                    color:white;
                    padding:10px 22px;
                    border-radius:16px;
                    display:inline-block;
                    font-size:22px;
                    font-weight:600;
                    margin-bottom:10px;">
                    {display_label}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Gauge
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
                    number={"font": {"size": 42}},
                    title={"text": ""},
                )
            )
            st.plotly_chart(fig, use_container_width=False)

            # Summary
            st.markdown(
                f"""
                <p style="font-size:16px; margin-top:10px;">
                Website <strong>{url}</strong> is classified as <strong>{display_label}</strong>.<br>
                Risk score: <strong>{risk_score:.1f} / 100</strong>
                </p>
                """,
                unsafe_allow_html=True,
            )

            # Key indicators (high level)
            st.markdown(
                """
                **Key signals used in this decision include:**
                - Domain age and trust history  
                - HTTPS / SSL configuration  
                - Security headers (HSTS, CSP)  
                - Google Safe Browsing blacklist checks  
                - Mixed-content and metadata indicators  
                """
            )

            # Log for history
            update_log(st.session_state, url, risk_class)

            # PDF report
            pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
            st.download_button(
                "📄 Download PDF Report",
                pdf_bytes,
                "fraudshield_report.pdf",
                mime="application/pdf",
            )

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Scan history at bottom of Scanner tab
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("📁 Recent Scan History")
    if "history" in st.session_state and len(st.session_state["history"]) > 0:
        st.dataframe(pd.DataFrame(st.session_state["history"]), use_container_width=True)
    else:
        st.write("No scans performed yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2️⃣ MODEL INTELLIGENCE TAB
# =========================================================
with tab_model:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("🧠 Model Intelligence Overview")

    st.write(
        """
FraudShield uses a hybrid machine-learning and rules-based risk engine.
The current deployed model evaluates each website using a compact set of
security and trust signals, then produces a probability-based risk score
between 0 and 100.
        """
    )

    # High-level metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Model Accuracy", "95%")
    col2.metric("AUC Score", "0.805")
    col3.metric("F1 Score", "0.91")

    st.markdown("---")

    st.markdown("### Model Input Signals")

    model_inputs = pd.DataFrame(
        [
            {
                "Input Feature": "Domain Age (days)",
                "Description": "Number of days since the domain was registered. New domains are more likely to be risky.",
            },
            {
                "Input Feature": "HTTPS Flag",
                "Description": "Whether the website enforces HTTPS. Lack of HTTPS is a strong negative trust signal.",
            },
            {
                "Input Feature": "HSTS Indicator",
                "Description": "Presence of HTTP Strict Transport Security (header or meta). Indicates stronger transport security.",
            },
            {
                "Input Feature": "CSP Indicator",
                "Description": "Presence of a Content Security Policy, which reduces script injection and malicious content.",
            },
            {
                "Input Feature": "Mixed Content Ratio",
                "Description": "Whether secure pages still load insecure resources. High ratios indicate poor security hygiene.",
            },
            {
                "Input Feature": "Safe Browsing Blacklist Flag",
                "Description": "Whether Google Safe Browsing has flagged the site as phishing or malware.",
            },
        ]
    )

    st.table(model_inputs)

    st.markdown("---")

    st.markdown("### Feature Importance (Illustrative)")

    feature_data = pd.DataFrame(
        {
            "Feature": [
                "Domain Age",
                "HTTPS / SSL",
                "Threatlist Match",
                "Security Headers (HSTS/CSP)",
                "Mixed Content",
            ],
            "Importance": [0.32, 0.24, 0.20, 0.16, 0.08],
        }
    )

    st.bar_chart(feature_data.set_index("Feature"))

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 3️⃣ API EXPLORER TAB
# =========================================================
with tab_api:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("🔌 API Explorer")

    st.write(
        "Use this panel to see the raw JSON response returned by the FraudShield scoring API."
    )

    api_url = st.text_input(
        "URL to test with API", placeholder="https://example.com", key="api_url_input"
    )

    if st.button("Call API", key="api_call_button"):
        with st.spinner("Calling FraudShield API…"):
            api_result = run_fraudshield_scan(api_url)

        if not api_result:
            st.error("API call failed. Please verify the backend is reachable.")
        else:
            st.write("**Raw API Response:**")
            st.json(api_result)

    st.markdown("---")

    st.markdown("### Integration Examples")

    st.write("**Python example:**")
    st.code(
        """
import requests

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"

payload = {"url": "https://example.com"}
response = requests.post(API_URL, json=payload)
print(response.json())
        """,
        language="python",
    )

    st.write("**cURL example:**")
    st.code(
        """
curl -X POST \\
  https://website-risk-scorer-api.onrender.com/scan_url \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}'
        """,
        language="bash",
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 4️⃣ THREAT CATEGORIES TAB
# =========================================================
with tab_threats:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("⚠️ Threat Categories")

    st.write(
        """
FraudShield not only assigns a numeric risk score, it also interprets the
signals into higher-level threat categories. These categories help platforms
like FindMe understand *why* a website is considered risky.
        """
    )

    categories = pd.DataFrame(
        [
            {
                "Threat Category": "Safe",
                "Description": "Signals are consistent with a legitimate, well-configured website.",
            },
            {
                "Threat Category": "Young Domain Risk",
                "Description": "Recently registered domains with limited trust history, modest risk score.",
            },
            {
                "Threat Category": "New Domain Fraud Risk",
                "Description": "Very young domains combined with elevated risk score, often linked to pop-up scams.",
            },
            {
                "Threat Category": "Weak Transport Security",
                "Description": "Lack of HTTPS or serious SSL issues, exposing users to interception and manipulation.",
            },
            {
                "Threat Category": "Mixed Content Exploitation Risk",
                "Description": "HTTPS pages loading insecure HTTP resources, allowing attackers to inject content.",
            },
            {
                "Threat Category": "High Fraud Likelihood",
                "Description": "Multiple negative signals and a high model score, strongly suggesting fraud or abuse.",
            },
            {
                "Threat Category": "Moderate Fraud Indicators",
                "Description": "Some risk factors present; requires caution when transacting.",
            },
            {
                "Threat Category": "Potential Fraud Indicators",
                "Description": "Non-ideal configuration with mild risk; monitored for escalation.",
            },
            {
                "Threat Category": "Phishing/Malware Source",
                "Description": "Direct match in Safe Browsing or similar lists; treated as a blacklisted threat.",
            },
        ]
    )

    st.table(categories)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 5️⃣ ARCHITECTURE TAB
# =========================================================
with tab_arch:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("🏗️ FraudShield System Architecture")

    st.write(
        """
FraudShield is structured as an end-to-end pipeline that can be easily
integrated into platforms like FindMe:
        """
    )

    st.markdown(
        """
1. **URL Ingestion**  
   The client (browser extension, platform, or API client) sends a website URL to the FraudShield API.

2. **Signal Extraction Layer**  
   The backend collects:
   - Domain age and registration data  
   - HTTPS and SSL configuration  
   - Security headers (HSTS, CSP)  
   - Mixed-content indicators  
   - Threat intelligence from Google Safe Browsing  

3. **Machine-Learning Probability Engine**  
   A trained classifier processes these features and produces a fraud-likelihood probability.

4. **Risk Calibration & Policy Layer**  
   The probability is adjusted based on domain age, SSL strength, and blacklist flags.  
   Blacklisted sites are automatically escalated.

5. **Classification & Explanation**  
   The final output includes:
   - Risk score (0–100)  
   - Risk class (Safe, Low Risk, Suspicious, High Risk, Blacklisted Threat)  
   - Underlying signals (domain age, HTTPS, HSTS, CSP, blacklist flag)  

6. **Delivery to Clients**  
   The result is returned to:
   - Chrome extension (real-time user warnings)  
   - Platforms such as FindMe (link safety checks)  
   - Dashboard (this interface) for analysis, demos, and reporting.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 6️⃣ RISK SCORING LOGIC TAB
# =========================================================
with tab_logic:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.subheader("📐 Risk Scoring Logic")

    st.write(
        """
FraudShield’s scoring engine converts security signals into an interpretable
0–100 risk score, then maps that score into the same labels used by the
Chrome extension.
        """
    )

    st.markdown("### Score → Class Mapping")

    mapping_df = pd.DataFrame(
        [
            {"Score Range": "0 – 10", "Class": "Safe"},
            {"Score Range": "10 – 40", "Class": "Low Risk"},
            {"Score Range": "40 – 70", "Class": "Suspicious"},
            {"Score Range": "70 – 95", "Class": "High Risk"},
            {"Score Range": "96 – 100 or blacklisted", "Class": "Blacklisted Threat"},
        ]
    )

    st.table(mapping_df)

    st.markdown("---")

    st.markdown("### Adjustments Applied Before Classification")

    st.markdown(
        """
The raw model probability is adjusted with straightforward rules:

- **Very old domains** (more than 10 years) → risk reduced  
- **HTTPS enabled** → risk reduced  
- **Safe Browsing blacklist flag** → score forced near 99 and labeled as Blacklisted Threat  

This combination of statistical prediction and clear safety rules helps
make the output stable, explainable, and suitable for real-world use
on platforms like FindMe.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown(
    "<p class='fs-footer'>FraudShield — Professional Real-Time Website Risk Evaluation</p>",
    unsafe_allow_html=True,
)
