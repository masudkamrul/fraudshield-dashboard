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
# CORPORATE CLEAN CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    body {
        background-color: #f5f6f8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .main-title {
        text-align: center;
        padding: 20px 0 5px 0;
    }

    .subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 15px;
    }

    .fs-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #e2e6ea;
        margin-bottom: 22px;
        box-shadow: 0 2px 5px rgba(15,23,42,0.03);
    }

    /* Section header bars */
    .section-header {
        padding: 10px 16px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        margin-bottom: 14px;
        font-size: 18px;
    }
    .section-blue { background: #2563eb; }
    .section-purple { background: #6d28d9; }
    .section-orange { background: #ea580c; }
    .section-green { background: #16a34a; }
    .section-red { background: #b91c1c; }
    .section-grey { background: #4b5563; }

    /* URL Input Style - scanner */
    .stTextInput>div>div>input {
        font-size: 18px !important;
        padding: 14px 16px !important;
        height: 55px !important;
        border-radius: 8px !important;
        border: 1.6px solid #b0b8c4 !important;
    }

    /* Info box */
    .info-box {
        background: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 14px;
        color: #374151;
        margin-top: 8px;
    }

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
st.markdown("<h1 class='main-title'>🛡️ FraudShield – Website Risk Evaluation Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Professional interface to demonstrate how FraudShield evaluates website safety using machine learning and security signals.</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# RISK CLASS → LABEL + COLOR (MATCHES EXTENSION)
# ---------------------------------------------------------
def map_risk_style(risk_class: str, blacklist_flag: int = 0):
    """
    Map backend risk_class + blacklist flag to the same
    labels & colors used in the Chrome extension.
    """

    # Blacklisted overrides everything
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

    # Fallback
    return "❓ Unknown", "#95a5a6"


# ---------------------------------------------------------
# TABS
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
# 1️⃣ SCANNER TAB — FINAL FIXED HERO SECTION
# =========================================================
import streamlit as st
import streamlit.components.v1 as components

with tab_scanner:

    # ---------------- HERO + SCANNER HTML ----------------
    hero_html = """
    <style>
        .hero-section {
            width: 100%;
            background: linear-gradient(90deg, #1F4E79, #1C6FB5);
            padding: 70px 20px 80px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 40px;
        }

        .hero-title {
            color: white;
            font-size: 38px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            color: #e2e8f0;
            font-size: 18px;
            margin-bottom: 35px;
        }

        .scan-container {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        .scan-box {
            display: flex;
            width: 720px;
            max-width: 95%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .scan-input {
            flex: 1;
            padding: 18px 20px;
            font-size: 18px;
            border: none;
            outline: none;
        }

        .scan-btn {
            background: #1C89C9;
            border: none;
            padding: 18px 28px;
            font-size: 17px;
            color: white;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
        }

        .scan-btn:hover {
            background: #166d9c;
        }
    </style>

    <div class="hero-section">
        <div class="hero-title">Free Website Malware & Security Scanner</div>
        <div class="hero-subtitle">
            Enter a website to check for vulnerabilities, fraud signals, and security issues.
        </div>

        <div class="scan-container">
            <div class="scan-box">
                <input type="text" id="fs_url" class="scan-input" placeholder="Enter your website domain">
                <button class="scan-btn" onclick="submitFraudShieldScan()">SCAN NOW</button>
            </div>
        </div>
    </div>

    <script>
        function submitFraudShieldScan() {
            const url = document.getElementById("fs_url").value;

            const hiddenInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
            hiddenInput.value = url;
            hiddenInput.dispatchEvent(new Event("input", { bubbles: true }));

            const hiddenBtn = window.parent.document.querySelector('button[data-scan="hidden"]');
            hiddenBtn.click();
        }
    </script>
    """

    # 🚀 Render HTML correctly (prevents escaping)
    components.html(hero_html, height=350)


    # ---------------- HIDDEN STREAMLIT FORM ----------------
    with st.form("fraudshield_hidden_form"):
        hidden_url = st.text_input("", key="fs_hidden_url", label_visibility="collapsed")
        run_scan = st.form_submit_button("SCAN NOW", kwargs={"data-scan": "hidden"})


    # ---------------- PROCESS THE SCAN ----------------
    if run_scan:
        if not hidden_url.strip():
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Scanning website…"):
                scan_result = run_fraudshield_scan(hidden_url)

            if not scan_result:
                st.error("Scan failed — API unreachable.")
            else:
                risk_class = scan_result.get("risk_class", "Unknown")
                risk_score = float(scan_result.get("risk_score", 0))
                blacklist_flag = scan_result.get("blacklist_flag", 0)

                label, color = map_risk_style(risk_class, blacklist_flag)

                st.markdown(
                    f"""
                    <div style="text-align:center;margin-top:25px;">
                        <span style="
                            background:{color};
                            color:white;
                            padding:14px 30px;
                            border-radius:25px;
                            font-size:24px;
                            font-weight:600;">
                            {label}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
                        number={"font": {"size": 48}}
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

                st.success(f"Risk Score: **{risk_score} / 100** — {label}")
                st.write(f"Scanned Website: **{hidden_url}**")
















# =========================================================
# 2️⃣ MODEL INTELLIGENCE TAB
# =========================================================
with tab_model:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-purple'>🧠 Model Intelligence</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield uses a compact but carefully designed machine-learning model
combined with rules, to convert security and trust signals into an interpretable
website risk score between 0 and 100.
        """
    )

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
                "Description": "Number of days since the domain was registered. New domains often correlate with scams.",
            },
            {
                "Input Feature": "HTTPS Flag",
                "Description": "Whether the website enforces HTTPS. Lack of HTTPS is a strong negative trust signal.",
            },
            {
                "Input Feature": "HSTS Indicator",
                "Description": "Presence of HTTP Strict Transport Security header/meta, indicating stronger transport security.",
            },
            {
                "Input Feature": "CSP Indicator",
                "Description": "Presence of a Content Security Policy, helping prevent script injection and content abuse.",
            },
            {
                "Input Feature": "Mixed Content Ratio",
                "Description": "Whether secure pages still load insecure HTTP resources.",
            },
            {
                "Input Feature": "Safe Browsing Blacklist Flag",
                "Description": "Whether Google Safe Browsing or a similar list has flagged the site as phishing/malware.",
            },
        ]
    )

    st.table(model_inputs)

    st.markdown("---")
    st.markdown("### Internal Feature Vector (Illustrative Code)")

    st.code(
        """
# Example of how internal features are prepared before scoring
features = [
    domain_age_days,   # e.g., 184
    https_flag,        # 1 if HTTPS is enabled, otherwise 0
    hsts_flag,         # 1 if HSTS header/meta detected
    csp_flag,          # 1 if CSP header/meta detected
    mixed_content_ratio  # value between 0 and 1
]
        """,
        language="python",
    )

    st.markdown("### Model Probability Computation (Illustrative)")

    st.code(
        """
# ML model predicts probability of fraud-like behavior
proba = model.predict_proba([features])[0][1]  # fraud-likelihood

# Convert to 0–100 scale
raw_score = proba * 100.0
        """,
        language="python",
    )

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
    st.markdown("<div class='section-header section-blue'>🔌 API Explorer</div>", unsafe_allow_html=True)

    st.write(
        "This section shows how external platforms like FindMe can directly query the FraudShield API."
    )

    api_url = st.text_input(
        "URL to test via API",
        placeholder="https://example.com",
        key="api_url_input"
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

    st.markdown("### Python Integration Example")

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

    st.markdown("### cURL Example")

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
    st.markdown("<div class='section-header section-orange'>⚠️ Threat Categories</div>", unsafe_allow_html=True)

    st.write(
        """
In addition to a numeric score, FraudShield interprets security signals into
higher-level threat categories. These labels help non-technical users quickly
understand the nature of the risk.
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
                "Description": "Recently registered domain with limited history; monitored for abuse.",
            },
            {
                "Threat Category": "New Domain Fraud Risk",
                "Description": "Very young domains and elevated risk scores, often seen in short-lived scam shops.",
            },
            {
                "Threat Category": "Weak Transport Security",
                "Description": "Lack of HTTPS or critical SSL issues, exposing users to interception.",
            },
            {
                "Threat Category": "Mixed Content Exploitation Risk",
                "Description": "HTTPS pages loading insecure HTTP resources, which attackers can tamper with.",
            },
            {
                "Threat Category": "High Fraud Likelihood",
                "Description": "Multiple negative signals and a high model score strongly indicate fraud.",
            },
            {
                "Threat Category": "Moderate Fraud Indicators",
                "Description": "Some warning signs present; caution recommended for transactions.",
            },
            {
                "Threat Category": "Phishing/Malware Source",
                "Description": "Known phishing or malware distribution, based on blacklist hits.",
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
    st.markdown("<div class='section-header section-green'>🏗️ System Architecture</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield is implemented as a modular pipeline that can be easily integrated
into platforms such as FindMe, browser extensions, and backend fraud engines.
        """
    )

    st.markdown(
        """
**High-Level Pipeline**

1. **URL Ingestion**  
   The client (e.g., browser extension or platform) sends the URL to the FraudShield API.

2. **Signal Extraction Layer**  
   The backend collects:
   - Domain registration age  
   - HTTPS / SSL configuration  
   - Security headers (HSTS, CSP)  
   - Mixed-content indicators  
   - Threat intelligence from Google Safe Browsing  

3. **Machine-Learning Probability Engine**  
   A trained classifier transforms these features into a fraud-likelihood probability.

4. **Risk Calibration & Policy Layer**  
   The probability is adjusted based on:
   - Domain age (older domains → lower risk)  
   - SSL/HTTPS presence (secure transport → lower risk)  
   - Blacklist flags (phishing/malware → forced to very high risk)  

5. **Classification & Explanation**  
   The pipeline outputs:
   - Risk score (0–100)  
   - Risk class (Safe, Low Risk, Suspicious, High Risk, Blacklisted Threat)  
   - Supporting signals and threat labels  

6. **Delivery to Clients**  
   Results are delivered to:
   - Chrome extension overlay (user warnings)  
   - Platforms like FindMe (link safety checks)  
   - This dashboard (for demonstration and analysis).  
        """
    )

    st.markdown("---")

    st.markdown("### Simplified Architecture (Code-Style View)")

    st.code(
        """
def score_url(url: str):
    signals = extract_signals(url)         # domain age, HTTPS, HSTS, CSP, mixed content, blacklist
    features = build_feature_vector(signals)
    proba = model.predict_proba([features])[0][1]  # ML probability
    score = calibrate_score(proba, signals)        # apply safety rules
    label = map_score_to_class(score, signals)     # Safe / Low / Suspicious / High / Blacklisted
    return score, label, signals
        """,
        language="python",
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 6️⃣ RISK SCORING LOGIC TAB
# =========================================================
with tab_logic:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-red'>📐 Risk Scoring Logic</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield combines the model’s probability output with a small set of
transparent safety rules. This makes the system more explainable and
suitable for real-world decision-making.
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
    st.markdown("### Risk Adjustments (Illustrative Code)")

    st.code(
        """
# Start from model-derived score (0–100)
score = raw_score

# Older domains → lower risk
if domain_age_days > 3650:       # more than 10 years
    score *= 0.75

# HTTPS present → slightly lower risk
if https_flag == 1:
    score *= 0.85

# High mixed-content ratio → increase risk
if mixed_content_ratio > 0.3:
    score *= 1.15

# Blacklist overrides everything
if blacklist_flag == 1:
    score = 99.0
        """,
        language="python",
    )

    st.markdown("### Threat Category Assignment (Illustrative Code)")

    st.code(
        """
if blacklist_flag == 1:
    threat_category = "Phishing/Malware Source"
elif score >= 80:
    threat_category = "High Fraud Likelihood"
elif score >= 60:
    threat_category = "Moderate Fraud Indicators"
elif https_flag == 0:
    threat_category = "Weak Transport Security"
elif mixed_content_ratio > 0.0:
    threat_category = "Mixed Content Exploitation Risk"
else:
    threat_category = "Safe or Low Risk"
        """,
        language="python",
    )

    st.markdown(
        """
These rules make the scoring process more interpretable for non-technical
stakeholders while still benefiting from machine-learning predictions.
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







