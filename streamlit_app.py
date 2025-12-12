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
# 1️⃣ SCANNER TAB — FINAL HERO SCANNER (PRODUCTION)
# =========================================================
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

with tab_scanner:

    hero_html = """
    <style>
        .hero {
            background: linear-gradient(135deg, #0f3c68, #1c6fb5);
            padding: 80px 20px 90px 20px;
            border-radius: 14px;
            text-align: center;
        }

        .hero h1 {
            color: white;
            font-size: 40px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .hero p {
            color: #dbeafe;
            font-size: 18px;
            margin-bottom: 40px;
        }

        .scan-box {
            max-width: 720px;
            margin: auto;
            background: white;
            border-radius: 10px;
            display: flex;
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        }

        .scan-box input {
            flex: 1;
            border: none;
            padding: 20px;
            font-size: 18px;
            outline: none;
        }

        .scan-box button {
            background: #1c89c9;
            color: white;
            border: none;
            padding: 0 34px;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
        }

        .scan-box button:hover {
            background: #166d9c;
        }

        .result-box {
            margin: 40px auto 0 auto;
            max-width: 560px;
            padding: 22px;
            border-radius: 14px;
            color: white;
            display: none;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25);
            transition: background 0.6s ease;
        }

        .bg-safe {
            background: linear-gradient(135deg, #2e7d32, #4caf50);
        }

        .bg-low {
            background: linear-gradient(135deg, #f9a825, #fbc02d);
        }

        .bg-suspicious {
            background: linear-gradient(135deg, #ef6c00, #ff9800);
        }

        .bg-high {
            background: linear-gradient(135deg, #c62828, #f44336);
        }

        .bg-blacklisted {
            background: linear-gradient(135deg, #4a0000, #b71c1c);
        }

        .risk-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .risk-score {
            font-size: 16px;
            margin-bottom: 12px;
        }

        .progress {
            width: 100%;
            height: 12px;
            background: rgba(255,255,255,0.35);
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: white;
            transition: width 1s ease;
        }
    </style>

    <div class="hero">
        <h1>Free Website Malware & Security Scanner</h1>
        <p>Enter a website to check for vulnerabilities, fraud signals, and security issues.</p>

        <div class="scan-box">
            <input id="scanUrl" placeholder="Enter your website domain (e.g. example.com)">
            <button onclick="runScan()">SCAN NOW</button>
        </div>

        <div id="result" class="result-box">
            <div class="risk-title" id="riskLabel"></div>
            <div class="risk-score" id="riskScore"></div>
            <div class="progress">
                <div class="progress-bar" id="riskBar"></div>
            </div>
        </div>
    </div>

    <script>
        function getBgClass(risk) {
            if (risk === "Safe") return "bg-safe";
            if (risk === "Low Risk") return "bg-low";
            if (risk === "Suspicious") return "bg-suspicious";
            if (risk === "High Risk") return "bg-high";
            return "bg-blacklisted";
        }

        async function runScan() {
            const url = document.getElementById("scanUrl").value;
            if (!url) return;

            const box = document.getElementById("result");
            box.style.display = "block";
            box.className = "result-box";

            document.getElementById("riskLabel").innerText = "Scanning…";
            document.getElementById("riskScore").innerText = "";
            document.getElementById("riskBar").style.width = "0%";

            try {
                const res = await fetch(
                    "https://website-risk-scorer-api.onrender.com/scan_url",
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url })
                    }
                );

                const data = await res.json();

                const risk = data.risk_class;
                const score = Number(data.risk_score).toFixed(2);

                box.classList.add(getBgClass(risk));

                document.getElementById("riskLabel").innerText = "Risk: " + risk;
                document.getElementById("riskScore").innerHTML =
                    "Risk Score: <strong>" + score + "%</strong>";

                document.getElementById("riskBar").style.width = score + "%";

            } catch (e) {
                box.classList.add("bg-high");
                document.getElementById("riskLabel").innerText =
                    "Scan failed. Please try again.";
            }
        }
    </script>
    """

    components.html(hero_html, height=620)
























# =========================================================
# 2️⃣ MODEL INTELLIGENCE TAB
# =========================================================
with tab_model:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-purple'>🧠 Model Intelligence</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield is a purpose-built fraud intelligence system that combines
machine-learning predictions with deterministic security rules to evaluate
the risk of deceptive, fraudulent, or unsafe websites in real time.
        """
    )

    # -----------------------------------------------------
    # EXECUTIVE PERFORMANCE METRICS
    # -----------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Model Accuracy", "95%")
    col2.metric("AUC Score", "0.805")
    col3.metric("F1 Score", "0.91")

    st.markdown(
        """
These metrics reflect balanced performance across detection accuracy,
false-positive control, and robustness when evaluating diverse real-world websites.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # MODEL INPUT SIGNALS
    # -----------------------------------------------------
    st.markdown("### 🔍 Model Input Signals")

    model_inputs = pd.DataFrame(
        [
            {
                "Input Feature": "Domain Age (days)",
                "Description": "Fraudulent websites are frequently registered shortly before being used in scams.",
            },
            {
                "Input Feature": "HTTPS / SSL Enforcement",
                "Description": "Lack of proper HTTPS configuration is a strong indicator of low trust.",
            },
            {
                "Input Feature": "HSTS Indicator",
                "Description": "HTTP Strict Transport Security signals enforcement of secure transport.",
            },
            {
                "Input Feature": "CSP Indicator",
                "Description": "Content Security Policy helps prevent malicious script injection.",
            },
            {
                "Input Feature": "Mixed Content Ratio",
                "Description": "Secure pages loading insecure resources increase exploitation risk.",
            },
            {
                "Input Feature": "Threat Intelligence Flag",
                "Description": "Known phishing or malware sources override probabilistic scoring.",
            },
        ]
    )

    st.table(model_inputs)

    st.markdown("---")

    # -----------------------------------------------------
    # REAL-WORLD FRAUD BEHAVIOR MAPPING
    # -----------------------------------------------------
    st.markdown("### 🌐 Mapping Model Signals to Real-World Fraud Behavior")

    fraud_mapping = pd.DataFrame(
        [
            {
                "Observed Fraud Pattern": "Short-lived scam storefronts",
                "Model Signal Used": "Domain Age",
                "Why It Matters": "Scam sites often disappear within weeks to avoid enforcement",
            },
            {
                "Observed Fraud Pattern": "Fake checkout or payment pages",
                "Model Signal Used": "HTTPS / SSL Misconfiguration",
                "Why It Matters": "Improper HTTPS exposes users during transactions",
            },
            {
                "Observed Fraud Pattern": "Credential harvesting sites",
                "Model Signal Used": "Missing CSP / HSTS",
                "Why It Matters": "Weak headers enable script injection and data theft",
            },
            {
                "Observed Fraud Pattern": "Malware and phishing campaigns",
                "Model Signal Used": "Threat Intelligence Flags",
                "Why It Matters": "Known malicious domains require immediate blocking",
            },
        ]
    )

    st.table(fraud_mapping)

    st.markdown("---")

    # -----------------------------------------------------
    # FEATURE ENGINEERING (ILLUSTRATIVE)
    # -----------------------------------------------------
    st.markdown("### 🧩 Feature Engineering (Illustrative)")

    st.write(
        """
Before inference, raw website signals are normalized and assembled into a
stable feature vector to ensure consistent scoring across environments.
        """
    )

    st.code(
        """
features = [
    domain_age_days,        # Integer
    https_flag,             # 1 if HTTPS enabled, else 0
    hsts_flag,              # 1 if HSTS detected
    csp_flag,               # 1 if CSP detected
    mixed_content_ratio     # Float between 0 and 1
]
        """,
        language="python",
    )

    st.markdown("### 📈 Probability Estimation")

    st.code(
        """
proba = model.predict_proba([features])[0][1]
raw_score = proba * 100.0
        """,
        language="python",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------
    st.markdown("### 📊 Feature Importance (Illustrative)")

    feature_data = pd.DataFrame(
        {
            "Feature": [
                "Domain Age",
                "HTTPS / SSL",
                "Threat Intelligence Match",
                "Security Headers (HSTS / CSP)",
                "Mixed Content",
            ],
            "Importance": [0.32, 0.24, 0.20, 0.16, 0.08],
        }
    )

    st.bar_chart(feature_data.set_index("Feature"))

    st.markdown(
        """
FraudShield prioritizes **infrastructure-level trust signals**, which are
significantly harder for attackers to manipulate than surface-level website content.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # LIVE INTERNET PERFORMANCE CONSIDERATIONS
    # -----------------------------------------------------
    st.markdown("### ⚙️ Performance in Live Internet Conditions")

    deployment_df = pd.DataFrame(
        [
            {
                "Design Consideration": "Real-time inference",
                "FraudShield Approach": "Lightweight features enable low-latency scoring",
            },
            {
                "Design Consideration": "Evasion resistance",
                "FraudShield Approach": "Relies on infrastructure signals costly for fraudsters to fake",
            },
            {
                "Design Consideration": "Data sparsity",
                "FraudShield Approach": "Does not require user history or traffic data",
            },
            {
                "Design Consideration": "Rapid fraud evolution",
                "FraudShield Approach": "Rules + ML allow fast updates without retraining",
            },
        ]
    )

    st.table(deployment_df)

    st.markdown("---")

    # -----------------------------------------------------
    # FALSE POSITIVE / FALSE NEGATIVE CONTROL
    # -----------------------------------------------------
    st.markdown("### 🎯 False Positive & False Negative Control")

    fp_fn_df = pd.DataFrame(
        [
            {
                "Risk Type": "False Positives",
                "Mitigation Strategy": "Gradual risk tiers instead of binary blocking",
            },
            {
                "Risk Type": "False Negatives",
                "Mitigation Strategy": "Threat intelligence overrides ML predictions",
            },
            {
                "Risk Type": "Ambiguous Websites",
                "Mitigation Strategy": "Classified as Suspicious rather than Safe",
            },
            {
                "Risk Type": "High-Confidence Threats",
                "Mitigation Strategy": "Automatically escalated to High Risk or Blacklisted",
            },
        ]
    )

    st.table(fp_fn_df)

    st.markdown("---")

    # -----------------------------------------------------
    # HUMAN-CENTERED INTERPRETABILITY
    # -----------------------------------------------------
    st.markdown("### 🧑‍💼 Human-Centered Risk Interpretation")

    human_df = pd.DataFrame(
        [
            {"Output Element": "Risk Score (%)", "Purpose": "Quantitative comparison across websites"},
            {"Output Element": "Risk Class", "Purpose": "Immediate human-readable decision"},
            {"Output Element": "Threat Category", "Purpose": "Explains why the site is risky"},
            {"Output Element": "Color Severity", "Purpose": "Visual urgency for rapid response"},
        ]
    )

    st.table(human_df)

    st.markdown("---")

    # -----------------------------------------------------
    # PLATFORM ALIGNMENT
    # -----------------------------------------------------
    st.markdown("### 🔗 Alignment with Platform Use Cases")

    platform_df = pd.DataFrame(
        [
            {
                "Platform Scenario": "User profile outbound links",
                "Model Benefit": "Evaluates third-party websites before users interact",
            },
            {
                "Platform Scenario": "Creator portfolios",
                "Model Benefit": "Reduces scams disguised as professional services",
            },
            {
                "Platform Scenario": "Marketplace redirects",
                "Model Benefit": "Detects fraudulent checkout environments",
            },
            {
                "Platform Scenario": "External engagement flows",
                "Model Benefit": "Preserves platform trust beyond hosted content",
            },
        ]
    )

    st.table(platform_df)

    st.markdown("---")

    # -----------------------------------------------------
    # GOVERNANCE & RESPONSIBLE AI
    # -----------------------------------------------------
    st.markdown("### 🔐 Model Governance & Responsible AI")

    governance_df = pd.DataFrame(
        [
            {
                "Governance Aspect": "Explainability",
                "Implementation": "Rules layered on ML probabilities",
            },
            {
                "Governance Aspect": "Bias Control",
                "Implementation": "No personal or demographic data used",
            },
            {
                "Governance Aspect": "Operational Safety",
                "Implementation": "Intermediate risk tiers enable escalation",
            },
            {
                "Governance Aspect": "Future Adaptability",
                "Implementation": "Designed for retraining as fraud patterns evolve",
            },
        ]
    )

    st.table(governance_df)

    st.markdown("---")

    # -----------------------------------------------------
    # WHY THIS IS NOT A GENERIC ML MODEL
    # -----------------------------------------------------
    st.markdown("### 🧠 Why This Is Not a Generic Machine-Learning Model")

    st.write(
        """
FraudShield is not a general-purpose data science experiment.
It is a preventive, real-time fraud intelligence system designed to protect
users from deceptive online environments before harm occurs.
        """
    )

    st.markdown(
        """
Key distinguishing characteristics include:

- Real-time operation during live browsing and platform interactions  
- Integration of machine learning with deterministic security rules  
- Infrastructure-level signals resistant to manipulation  
- Designed for deployment across consumer platforms and enterprises  
- Direct alignment with cybersecurity and consumer-protection objectives  
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)












# =========================================================
# 3️⃣ API EXPLORER TAB (UPGRADED FOR ENTERPRISE DEMO)
# =========================================================
with tab_api:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-blue'>🔌 API Explorer</div>", unsafe_allow_html=True)

    st.write(
        """
This section demonstrates how external platforms can integrate FraudShield
as a lightweight safety layer for outbound links. It includes live testing, response inspection,
latency visibility, and batch-evaluation workflows that mirror real platform needs.
        """
    )

    # -----------------------------------------------------
    # API CONFIG (CENTRALIZED)
    # -----------------------------------------------------
    API_ENDPOINT = "https://website-risk-scorer-api.onrender.com/scan_url"

    st.markdown("### ✅ API Endpoint")
    st.code(API_ENDPOINT)

    st.markdown(
        """
<div class="info-box">
<strong>Typical integration goal:</strong> When a user posts or clicks an outbound link, the platform calls the API
to get a risk score & classification. This enables warnings, moderation flags, or safer navigation experiences.
</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -----------------------------------------------------
    # LIVE SINGLE URL TEST + LATENCY
    # -----------------------------------------------------
    st.markdown("### 🧪 Live API Test (Single URL)")

    colA, colB = st.columns([3, 1])
    with colA:
        api_url = st.text_input(
            "Website URL to test",
            placeholder="https://example.com",
            key="api_url_input"
        )
    with colB:
        st.write("")
        st.write("")
        run_live = st.button("Call API", key="api_call_button", use_container_width=True)

    if run_live:
        if not api_url.strip():
            st.error("Please enter a valid URL.")
        else:
            import time
            start = time.time()
            with st.spinner("Calling FraudShield API…"):
                api_result = run_fraudshield_scan(api_url)
            elapsed_ms = (time.time() - start) * 1000.0

            if not api_result:
                st.error("API call failed. Please verify the backend is reachable.")
            else:
                # Basic extract for display
                risk_class = api_result.get("risk_class", "Unknown")
                risk_score = float(api_result.get("risk_score", 0))
                blacklist_flag = api_result.get("blacklist_flag", 0)

                label, color = map_risk_style(risk_class, blacklist_flag)

                # Summary card
                st.markdown(
                    f"""
<div style="
    border:1px solid #e2e6ea;
    border-left:6px solid {color};
    border-radius:10px;
    padding:14px 16px;
    background:#ffffff;
    margin-top:10px;">
    <div style="font-size:16px; font-weight:700; margin-bottom:6px;">API Result Summary</div>
    <div style="font-size:14px;">
        <strong>URL:</strong> {api_url}<br>
        <strong>Classification:</strong> <span style="color:{color}; font-weight:700;">{label}</span><br>
        <strong>Risk Score:</strong> <span style="font-weight:700;">{risk_score:.2f}%</span><br>
        <strong>Latency:</strong> {elapsed_ms:.0f} ms
    </div>
</div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("#### Raw API Response (JSON)")
                st.json(api_result)

    st.markdown("---")

    # -----------------------------------------------------
    # RESPONSE CONTRACT (SCHEMA)
    # -----------------------------------------------------
    st.markdown("### 📄 API Response Contract (What Integrators Can Rely On)")

    st.write(
        """
Below is an example response structure to help platform teams implement stable parsing and UI logic.
(Fields may expand over time, but core fields should remain consistent.)
        """
    )

    st.code(
        """
{
  "url": "https://example.com",
  "risk_class": "Low Risk",
  "risk_score": 32.50,
  "blacklist_flag": 0,
  "signals": {
      "domain_age_days": 1840,
      "https_flag": 1,
      "hsts_flag": 1,
      "csp_flag": 1,
      "mixed_content_ratio": 0.00
  }
}
        """,
        language="json"
    )

    st.markdown("---")

    # -----------------------------------------------------
    # INTEGRATION PATTERNS (REAL PLATFORM USE)
    # -----------------------------------------------------
    st.markdown("### 🧩 Real-World Integration Patterns (Platform Examples)")

    patterns = pd.DataFrame(
        [
            {
                "Pattern": "Outbound Link Pre-Click Check",
                "What Happens": "User clicks a link → platform calls API → show warning screen if risky",
                "Why It Helps": "Prevents harm before users enter unknown websites",
            },
            {
                "Pattern": "Profile Link Safety Badge",
                "What Happens": "On profile pages, show Safe/Low/Suspicious badges next to external links",
                "Why It Helps": "Builds trust + transparency for viewers and customers",
            },
            {
                "Pattern": "Content Moderation Queue",
                "What Happens": "If risk ≥ threshold, automatically flag link for manual review",
                "Why It Helps": "Reduces platform abuse and protects brand reputation",
            },
            {
                "Pattern": "Background Batch Verification",
                "What Happens": "Nightly scan of newly added/updated links and store outcomes",
                "Why It Helps": "Scales safety without adding friction in user workflows",
            },
        ]
    )

    st.table(patterns)

    st.markdown("---")

    # -----------------------------------------------------
    # BATCH SCAN DEMO 
    # -----------------------------------------------------
    st.markdown("### 📦 Batch Scan Demo")

    st.write(
        """
Paste multiple URLs (one per line) to simulate scanning outbound links across profiles or posts.
This mirrors real platform needs such as scanning user-submitted links in bulk.
        """
    )

    batch_text = st.text_area(
        "Paste URLs (one per line)",
        placeholder="https://example.com\nhttps://another-site.com\nhttps://shop.example.org",
        height=140,
        key="batch_urls"
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        run_batch = st.button("Run Batch Scan", use_container_width=True, key="run_batch_scan")
    with col2:
        st.caption("Tip: This is useful to validate behavior across multiple real-world websites quickly.")

    if run_batch:
        urls = [u.strip() for u in batch_text.splitlines() if u.strip()]
        if len(urls) == 0:
            st.error("Please paste at least one URL.")
        else:
            rows = []
            with st.spinner(f"Scanning {len(urls)} URLs…"):
                import time
                for u in urls[:50]:  # safety cap for demos
                    t0 = time.time()
                    r = run_fraudshield_scan(u)
                    latency = (time.time() - t0) * 1000.0

                    if not r:
                        rows.append({"url": u, "risk_class": "API_ERROR", "risk_score": None, "latency_ms": round(latency, 0)})
                        continue

                    rc = r.get("risk_class", "Unknown")
                    rs = float(r.get("risk_score", 0))
                    bl = r.get("blacklist_flag", 0)
                    label, _ = map_risk_style(rc, bl)

                    rows.append(
                        {
                            "url": u,
                            "risk_class": label,
                            "risk_score_%": round(rs, 2),
                            "latency_ms": round(latency, 0),
                        }
                    )

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "⬇️ Download Batch Results (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                file_name="fraudshield_batch_results.csv",
                mime="text/csv",
            )

    st.markdown("---")

    # -----------------------------------------------------
    # COPY-PASTE SNIPPETS (PYTHON / JS / CURL)
    # -----------------------------------------------------
    st.markdown("### 🧾 Copy-Paste Integration Snippets")

    st.markdown("#### Python (Server-side integration)")
    st.code(
        f"""
import requests

API_URL = "{API_ENDPOINT}"

payload = {{"url": "https://example.com"}}
res = requests.post(API_URL, json=payload, timeout=15)
res.raise_for_status()
data = res.json()

print("risk_class:", data.get("risk_class"))
print("risk_score:", data.get("risk_score"))
print("blacklist_flag:", data.get("blacklist_flag"))
        """,
        language="python",
    )

    st.markdown("#### JavaScript (Platform / service integration)")
    st.code(
        f"""
async function scanUrl(url) {{
  const res = await fetch("{API_ENDPOINT}", {{
    method: "POST",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify({{ url }})
  }});

  if (!res.ok) throw new Error("API error");
  const data = await res.json();
  return data; // {{ risk_class, risk_score, blacklist_flag, ... }}
}}

scanUrl("https://example.com").then(console.log);
        """,
        language="javascript",
    )

    st.markdown("#### cURL (Quick testing)")
    st.code(
        f"""
curl -X POST "{API_ENDPOINT}" \\
  -H "Content-Type: application/json" \\
  -d '{{"url":"https://example.com"}}'
        """,
        language="bash",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # OPERATIONAL NOTES (PROFESSIONAL)
    # -----------------------------------------------------
    st.markdown("### 🛡️ Operational Notes for Production Use")

    ops_df = pd.DataFrame(
        [
            {"Best Practice": "Timeouts", "Recommendation": "Use 10–20s client timeout for stability"},
            {"Best Practice": "Retries", "Recommendation": "Retry once on transient network failures"},
            {"Best Practice": "Caching", "Recommendation": "Cache results per URL to reduce repeated calls"},
            {"Best Practice": "Rate Limiting", "Recommendation": "Apply throttling for platform-wide batch jobs"},
            {"Best Practice": "Threshold Policy", "Recommendation": "Define actions per tier: Safe/Low/Suspicious/High"},
        ]
    )

    st.table(ops_df)

    st.markdown(
        """
<div class="info-box">
<strong>Integration-ready takeaway:</strong>
FraudShield can be used as an on-demand risk oracle for outbound links — enabling warnings,
badges, moderation workflows, and safer navigation experiences without changing how users
normally use the platform.
</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)











# =========================================================
# 4️⃣ THREAT CATEGORIES TAB (UPGRADED: PLATFORM SAFETY TAXONOMY)
# =========================================================
with tab_threats:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-orange'>⚠️ Threat Categories</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield does more than output a numeric risk score. It also maps observed trust and safety
signals into **human-readable threat categories**. This makes the system usable for
non-technical stakeholders and enables clear platform actions such as warnings, badges, or moderation.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # THREAT TAXONOMY TABLE (CATEGORY + SEVERITY + ACTIONS)
    # -----------------------------------------------------
    st.markdown("### 🧭 Threat Taxonomy (Category → Meaning → Recommended Action)")

    taxonomy = pd.DataFrame(
        [
            {
                "Threat Category": "Safe",
                "Severity": "✅ Minimal",
                "What It Means": "The website appears consistent with legitimate infrastructure and baseline security expectations.",
                "Recommended Platform Action": "Allow normal navigation. Optional: show a green trust badge."
            },
            {
                "Threat Category": "Low Risk",
                "Severity": "🟡 Low",
                "What It Means": "Minor concerns or limited history. Not clearly malicious, but caution is appropriate for transactions.",
                "Recommended Platform Action": "Allow navigation. Optional: display a “Low Risk” badge; encourage cautious checkout."
            },
            {
                "Threat Category": "Young Domain Risk",
                "Severity": "🟠 Elevated",
                "What It Means": "Recently registered domain with limited reputation history; frequently associated with short-lived scam campaigns.",
                "Recommended Platform Action": "Show a caution banner. For commerce links, recommend verifying seller identity before paying."
            },
            {
                "Threat Category": "New Domain Fraud Risk",
                "Severity": "🔶 High",
                "What It Means": "Very new domains combined with stronger warning signals—commonly seen in fake storefronts and deceptive product pages.",
                "Recommended Platform Action": "Show interstitial warning page. Consider flagging the link for moderation review."
            },
            {
                "Threat Category": "Weak Transport Security",
                "Severity": "🔶 High",
                "What It Means": "Missing or weak HTTPS/SSL protection increases interception risk, especially for logins or payments.",
                "Recommended Platform Action": "Warn users before entering sensitive data. For payments, recommend avoiding the site."
            },
            {
                "Threat Category": "Mixed Content Exploitation Risk",
                "Severity": "🟠 Elevated",
                "What It Means": "The page loads insecure resources which can be modified in transit, creating script injection and content tampering risk.",
                "Recommended Platform Action": "Warn users. Allow navigation but caution against entering credentials or payment details."
            },
            {
                "Threat Category": "Moderate Fraud Indicators",
                "Severity": "🟠 Elevated",
                "What It Means": "Multiple caution signals are present. The website may be deceptive or unsafe for commercial activity.",
                "Recommended Platform Action": "Show warning banner or interstitial. Consider risk-based friction (extra confirmation click)."
            },
            {
                "Threat Category": "High Fraud Likelihood",
                "Severity": "🔴 Critical",
                "What It Means": "The website exhibits strong patterns consistent with fraudulent behavior (e.g., scam storefront indicators).",
                "Recommended Platform Action": "Strong interstitial warning. Recommend users do not proceed. Queue link for moderation."
            },
            {
                "Threat Category": "Phishing/Malware Source",
                "Severity": "☠️ Severe",
                "What It Means": "The domain is flagged by threat intelligence sources as malicious (phishing or malware distribution).",
                "Recommended Platform Action": "Block by default. Present a high-severity warning. Remove or quarantine the link."
            },
        ]
    )

    st.table(taxonomy)

    st.markdown("---")

    # -----------------------------------------------------
    # REAL-WORLD EXAMPLES (NON-TECHNICAL, BUSINESS-FACING)
    # -----------------------------------------------------
    st.markdown("### 🌍 Real-World Examples (Why These Categories Matter)")

    examples = pd.DataFrame(
        [
            {
                "Scenario": "Portfolio link to an external store",
                "Potential Risk": "A fake storefront imitates legitimate brands and collects payments without delivery",
                "FraudShield Category": "New Domain Fraud Risk / High Fraud Likelihood",
                "Impact": "Prevents user harm and protects platform reputation"
            },
            {
                "Scenario": "Service booking link on a profile",
                "Potential Risk": "A spoofed booking page requests deposits or personal data",
                "FraudShield Category": "Moderate Fraud Indicators / Phishing Risk",
                "Impact": "Reduces scams targeting consumers through trusted profiles"
            },
            {
                "Scenario": "“Contact me” link directing to login form",
                "Potential Risk": "Credential harvesting (phishing) disguised as messaging or sign-in",
                "FraudShield Category": "Phishing/Malware Source (if flagged) or High Fraud Likelihood",
                "Impact": "Prevents account compromise and downstream fraud"
            },
            {
                "Scenario": "External tool link for a small business",
                "Potential Risk": "Weak HTTPS or mixed content causes data leakage risk",
                "FraudShield Category": "Weak Transport Security / Mixed Content Risk",
                "Impact": "Improves safety posture even when content is not malicious"
            },
        ]
    )

    st.table(examples)

    st.markdown("---")

    # -----------------------------------------------------
    # ACTION POLICY MATRIX 
    # -----------------------------------------------------
    st.markdown("### 🧩 Platform Action Policy Matrix")

    policy = pd.DataFrame(
        [
            {"Risk Tier": "Safe", "Badge": "Green badge", "UI Action": "No friction", "Moderation": "No"},
            {"Risk Tier": "Low Risk", "Badge": "Yellow badge", "UI Action": "Soft caution", "Moderation": "No"},
            {"Risk Tier": "Elevated", "Badge": "Orange badge", "UI Action": "Warning banner", "Moderation": "Optional"},
            {"Risk Tier": "High", "Badge": "Red badge", "UI Action": "Interstitial warning + confirm", "Moderation": "Yes"},
            {"Risk Tier": "Severe", "Badge": "Black/Red", "UI Action": "Block or quarantine link", "Moderation": "Yes (priority)"},
        ]
    )
    st.table(policy)

    st.markdown("---")

    # -----------------------------------------------------
    # USER-FACING MESSAGE TEMPLATES (VERY USEFUL FOR REAL PLATFORM)
    # -----------------------------------------------------
    st.markdown("### 🗣️ User Warning Message Templates (Ready to Use)")

    msg_df = pd.DataFrame(
        [
            {
                "Tier": "Low Risk",
                "Suggested Message": "This link has limited trust history. Proceed with caution, especially for payments."
            },
            {
                "Tier": "Elevated",
                "Suggested Message": "This website shows warning signs. Avoid entering sensitive information unless you trust the source."
            },
            {
                "Tier": "High",
                "Suggested Message": "High-risk website detected. We recommend you do not proceed."
            },
            {
                "Tier": "Severe",
                "Suggested Message": "Dangerous website detected (phishing/malware risk). This link is blocked for your safety."
            },
        ]
    )
    st.table(msg_df)

    st.markdown("---")

    # -----------------------------------------------------
    # TRANSPARENT TRIAGE LOGIC (ILLUSTRATIVE)
    # -----------------------------------------------------
    st.markdown("### 🧠 How Categories Are Assigned (High-Level, Interpretable)")

    st.write(
        """
FraudShield uses an interpretable triage approach:  
- **Threat intelligence flags** can override normal scoring (safety-first).  
- Otherwise, risk categories align with the **risk score bands** and a small set of security signals.
        """
    )

    st.code(
        """
if blacklist_flag == 1:
    category = "Phishing/Malware Source"
elif risk_score >= 80:
    category = "High Fraud Likelihood"
elif risk_score >= 60:
    category = "Moderate Fraud Indicators"
elif https_flag == 0:
    category = "Weak Transport Security"
elif mixed_content_ratio > 0:
    category = "Mixed Content Exploitation Risk"
elif domain_age_days < 30:
    category = "New Domain Fraud Risk"
elif domain_age_days < 180:
    category = "Young Domain Risk"
else:
    category = "Safe / Low Risk"
        """,
        language="python",
    )

    st.markdown(
        """
This structure is intentionally designed to be **usable by platforms**: it supports
consistent user messaging, moderation policies, and safety experiences.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)













# =========================================================
# 5️⃣ SYSTEM ARCHITECTURE TAB (ENTERPRISE-GRADE)
# =========================================================
with tab_arch:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header section-green'>🏗️ System Architecture</div>",
        unsafe_allow_html=True
    )

    st.write(
        """
FraudShield is designed as a **modular, API-first security architecture** that can be
embedded into a wide range of digital products, consumer platforms, and enterprise systems.
The architecture emphasizes **scalability, explainability, and safety-first decision making**.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # HIGH-LEVEL ARCHITECTURE OVERVIEW
    # -----------------------------------------------------
    st.markdown("### 🔍 High-Level Architecture Overview")

    st.write(
        """
At a high level, FraudShield operates as a **real-time risk evaluation pipeline**.
Each component is independently scalable and can evolve without disrupting the rest
of the system.
        """
    )

    st.markdown(
        """
**End-to-End Flow**

1. **Client Request Layer**  
   A client submits a URL for evaluation (e.g., browser extension, dashboard, backend service).

2. **API Gateway & Validation**  
   Requests pass through a gateway that performs:
   - Input validation and normalization  
   - Rate limiting and abuse prevention  
   - Authentication (for partner or internal use)

3. **Signal Collection & Enrichment Layer**  
   The system gathers trust and security signals from multiple sources.

4. **Risk Intelligence Engine**  
   Signals are converted into structured features and evaluated by the ML model
   and rule-based safety policies.

5. **Decision & Classification Layer**  
   The system produces interpretable outputs (score, category, explanation).

6. **Delivery & Integration Layer**  
   Results are returned in a platform-friendly format suitable for UI warnings,
   moderation systems, or automated decision pipelines.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # SIGNAL EXTRACTION LAYER (DETAILED)
    # -----------------------------------------------------
    st.markdown("### 🧩 Signal Extraction & Enrichment Layer")

    st.write(
        """
This layer transforms a raw URL into **structured trust signals**.  
It is intentionally extensible so new signals can be added without retraining
the core model.
        """
    )

    signal_df = pd.DataFrame(
        [
            {
                "Signal Type": "Domain Intelligence",
                "Examples": "Domain age, registrar reputation, lifecycle indicators",
                "Why It Matters": "Fraud campaigns often rely on newly registered or frequently rotated domains"
            },
            {
                "Signal Type": "Transport Security",
                "Examples": "HTTPS status, SSL validity, protocol strength",
                "Why It Matters": "Weak or missing encryption increases interception and impersonation risk"
            },
            {
                "Signal Type": "Security Headers",
                "Examples": "HSTS, CSP, X-Content-Type-Options",
                "Why It Matters": "Modern legitimate sites typically deploy baseline security headers"
            },
            {
                "Signal Type": "Content Integrity",
                "Examples": "Mixed content indicators, insecure resource loading",
                "Why It Matters": "Mixed content enables script injection and content manipulation"
            },
            {
                "Signal Type": "Threat Intelligence",
                "Examples": "Phishing or malware blacklist hits",
                "Why It Matters": "Known malicious infrastructure should override normal risk scoring"
            },
        ]
    )
    st.table(signal_df)

    st.markdown("---")

    # -----------------------------------------------------
    # RISK INTELLIGENCE ENGINE
    # -----------------------------------------------------
    st.markdown("### 🧠 Risk Intelligence Engine")

    st.write(
        """
FraudShield intentionally combines **machine-learning inference** with
**transparent rule-based policies**. This hybrid approach balances accuracy
with explainability and operational safety.
        """
    )

    st.markdown(
        """
**Why Hybrid Intelligence?**

- Pure ML models can be opaque and brittle under adversarial conditions  
- Rule-only systems fail to generalize to novel fraud patterns  
- Hybrid systems provide **predictive power + deterministic safeguards**
        """
    )

    st.code(
        """
# Conceptual evaluation flow

signals = extract_signals(url)
features = build_feature_vector(signals)

# Machine-learning probability
fraud_probability = model.predict_proba([features])[0][1]

# Convert to risk score
raw_score = fraud_probability * 100

# Policy-based calibration
final_score = apply_safety_policies(raw_score, signals)

# Classification
risk_class = map_score_to_category(final_score, signals)
        """,
        language="python",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # POLICY & GOVERNANCE LAYER
    # -----------------------------------------------------
    st.markdown("### 🛡️ Policy, Governance & Safety Controls")

    st.write(
        """
This layer ensures the system behaves **conservatively and predictably**
in high-risk situations.
        """
    )

    policy_df = pd.DataFrame(
        [
            {
                "Control": "Blacklist Override",
                "Purpose": "Immediately elevate risk when known malicious indicators are present"
            },
            {
                "Control": "Score Calibration",
                "Purpose": "Adjust raw ML output using domain age and security posture"
            },
            {
                "Control": "Fail-Safe Defaults",
                "Purpose": "Avoid false negatives when data is incomplete or unavailable"
            },
            {
                "Control": "Explainable Categories",
                "Purpose": "Ensure outputs are understandable by non-technical users"
            },
        ]
    )
    st.table(policy_df)

    st.markdown("---")

    # -----------------------------------------------------
    # SCALABILITY & DEPLOYMENT MODEL
    # -----------------------------------------------------
    st.markdown("### 🚀 Scalability & Deployment Model")

    st.write(
        """
FraudShield is designed to operate at **internet scale** with predictable latency.
        """
    )

    deploy_df = pd.DataFrame(
        [
            {
                "Layer": "API Layer",
                "Design Choice": "Stateless REST API",
                "Benefit": "Horizontal scaling and low-latency responses"
            },
            {
                "Layer": "Model Inference",
                "Design Choice": "Lightweight feature vector + compact model",
                "Benefit": "Fast execution suitable for real-time use"
            },
            {
                "Layer": "Threat Intelligence",
                "Design Choice": "Cached lookups + periodic refresh",
                "Benefit": "Reduced external dependency latency"
            },
            {
                "Layer": "Observability",
                "Design Choice": "Request logging & metrics",
                "Benefit": "Auditability, tuning, and incident analysis"
            },
        ]
    )
    st.table(deploy_df)

    st.markdown("---")

    # -----------------------------------------------------
    # INTEGRATION PATTERNS
    # -----------------------------------------------------
    st.markdown("### 🔌 Common Integration Patterns")

    st.write(
        """
The architecture supports multiple real-world integration patterns without modification.
        """
    )

    st.markdown(
        """
- **Browser-Side Protection**  
  Real-time warnings when users navigate to risky destinations.

- **Platform Safety Layer**  
  Evaluate outbound links before allowing transactions or interactions.

- **Moderation & Trust Pipelines**  
  Feed risk signals into review queues or automated enforcement rules.

- **Analytics & Compliance**  
  Aggregate risk trends for reporting and continuous improvement.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # ARCHITECTURAL PRINCIPLES
    # -----------------------------------------------------
    st.markdown("### 🧱 Core Architectural Principles")

    principles = pd.DataFrame(
        [
            {"Principle": "Safety-First", "Description": "Bias toward protecting users over convenience"},
            {"Principle": "Explainability", "Description": "Outputs must be understandable by non-experts"},
            {"Principle": "Extensibility", "Description": "New signals can be added without re-architecture"},
            {"Principle": "Vendor Neutrality", "Description": "No dependency on a single platform or ecosystem"},
            {"Principle": "Low Friction", "Description": "Minimal latency and integration effort"},
        ]
    )
    st.table(principles)

    st.markdown(
        """
This architecture positions FraudShield as a **general-purpose trust and safety
component** suitable for modern digital platforms operating at scale.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)












# =========================================================
# 6️⃣ RISK SCORING LOGIC TAB (ENTERPRISE-GRADE)
# =========================================================
with tab_logic:
    st.markdown("<div class='fs-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header section-red'>📐 Risk Scoring Logic</div>", unsafe_allow_html=True)

    st.write(
        """
FraudShield uses a **defense-in-depth scoring framework** that combines:
(1) model-derived risk probability, (2) deterministic safety policies, and
(3) quality controls that prevent misleading results when signals are incomplete.

This hybrid approach is common in real-world Trust & Safety systems because it is:
**predictive**, **explainable**, and **operationally safe** under adversarial conditions.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 1) SCORE LIFECYCLE
    # -----------------------------------------------------
    st.markdown("### 1) Risk Score Lifecycle (How a URL becomes a decision)")

    st.markdown(
        """
**Step A — Normalize & Validate**  
The URL is normalized (scheme, domain extraction) and checked for obvious input issues.

**Step B — Collect Signals**  
Signals are gathered (domain age, transport security posture, header indicators, threat intelligence flags, etc.).

**Step C — Model Inference**  
A trained classifier produces a fraud-likelihood probability (0–1).

**Step D — Policy Calibration**  
Transparent policies adjust raw probability into a final score (0–100) to enforce safety guarantees.

**Step E — Decision Tier & Explanation**  
The system returns (score, class) plus a short explanation and recommended action.
        """
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 2) SCORE → CLASS MAPPING + RECOMMENDED ACTIONS
    # -----------------------------------------------------
    st.markdown("### 2) Score → Class Mapping (with recommended action)")

    mapping_df = pd.DataFrame(
        [
            {"Score Range": "0 – 10", "Class": "Safe", "Suggested Action": "Allow", "User Guidance": "Normal browsing expected."},
            {"Score Range": "10 – 40", "Class": "Low Risk", "Suggested Action": "Allow + Monitor", "User Guidance": "Proceed with standard caution."},
            {"Score Range": "40 – 70", "Class": "Suspicious", "Suggested Action": "Warn", "User Guidance": "Avoid payments; verify legitimacy before continuing."},
            {"Score Range": "70 – 95", "Class": "High Risk", "Suggested Action": "Strong Warn / Block (context-dependent)", "User Guidance": "High likelihood of scam behavior."},
            {"Score Range": "96 – 100 or blacklisted", "Class": "Blacklisted Threat", "Suggested Action": "Block", "User Guidance": "Known malicious/phishing/malware signal present."},
        ]
    )
    st.table(mapping_df)

    st.markdown("---")

    # -----------------------------------------------------
    # 3) SAFETY POLICIES (ENTERPRISE CONTROLS)
    # -----------------------------------------------------
    st.markdown("### 3) Safety Policies (Deterministic controls used in production systems)")

    st.write(
        """
Safety policies ensure the system behaves predictably in high-risk scenarios.
They also reduce false negatives when attackers attempt to “look normal.”
        """
    )

    policy_df = pd.DataFrame(
        [
            {"Policy Control": "Threat Intelligence Override", "Purpose": "If a domain matches a trusted blacklist, force the highest tier regardless of ML output."},
            {"Policy Control": "New Domain Elevation", "Purpose": "Very young domains receive a risk lift because many fraud campaigns rely on short-lived domains."},
            {"Policy Control": "Security Posture Penalty", "Purpose": "Missing HTTPS or weak security headers increases risk due to poor trust signals."},
            {"Policy Control": "Signal Quality Fallback", "Purpose": "If key signals cannot be obtained, avoid over-confident 'Safe' ratings."},
            {"Policy Control": "Score Smoothing", "Purpose": "Prevent extreme oscillations for borderline cases to keep user experience consistent."},
        ]
    )
    st.table(policy_df)

    st.markdown("---")

    # -----------------------------------------------------
    # 4) CONFIDENCE & SIGNAL QUALITY (IMPORTANT FOR REAL WORLD)
    # -----------------------------------------------------
    st.markdown("### 4) Confidence Handling (Signal Quality & Safe Defaults)")

    st.write(
        """
Real-world scanners sometimes face missing or unreliable signals (timeouts, blocked headers, DNS issues).
FraudShield can expose a **confidence level** (high/medium/low) to prevent misleading outcomes.

**Example principle:**  
If signal quality is low, FraudShield avoids returning “Safe” unless there is strong evidence.
        """
    )

    st.code(
        """
# Illustrative confidence logic (conceptual)

signal_coverage = collected_signals / expected_signals   # e.g., 0.65
latency_ms = request_latency_ms

if signal_coverage < 0.60:
    confidence = "LOW"
elif signal_coverage < 0.85:
    confidence = "MEDIUM"
else:
    confidence = "HIGH"

# Safe-default: do not emit "Safe" when confidence is LOW
if confidence == "LOW" and risk_class == "Safe":
    risk_class = "Low Risk"
        """,
        language="python",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 5) CALIBRATION & ADJUSTMENTS (BETTER THAN SIMPLE MULTIPLIERS)
    # -----------------------------------------------------
    st.markdown("### 5) Risk Calibration (Policy-based score shaping)")

    st.write(
        """
Instead of relying only on a raw ML score, calibration shapes the final score so it matches
real-world expectations and safety requirements.
        """
    )

    st.code(
        """
# Illustrative calibration logic (conceptual)

score = raw_score  # 0..100 from model probability

# 1) Threat intelligence override
if blacklist_flag == 1:
    score = 99.0

# 2) New domain uplift (example)
if domain_age_days is not None:
    if domain_age_days < 30:
        score = max(score, 85.0)   # very young: strongly suspicious by policy
    elif domain_age_days < 180:
        score = max(score, 60.0)   # new-ish: elevated baseline
    elif domain_age_days > 3650:
        score *= 0.80              # mature domains reduce risk, not eliminate it

# 3) Transport security penalty
if https_flag == 0:
    score = min(100.0, score + 12.0)

# 4) Security header posture shaping
header_score = (hsts_flag + csp_flag)  # simple proxy
if header_score == 0:
    score = min(100.0, score + 6.0)

# 5) Mixed content penalty
if mixed_content_ratio is not None and mixed_content_ratio > 0.30:
    score = min(100.0, score + 8.0)

score = max(0.0, min(100.0, score))
        """,
        language="python",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 6) DECISION OUTPUT (WHAT PARTNERS/USERS NEED)
    # -----------------------------------------------------
    st.markdown("### 6) Decision Output (What a consuming system receives)")

    st.write(
        """
A production-ready risk engine should return more than a number. FraudShield is structured to return:
- **Risk Score (0–100)**  
- **Risk Class (tier label)**  
- **Suggested Action (allow / monitor / warn / block)**  
- **Short Explanation (human-readable)**  
- **Confidence (high/medium/low)**  
This enables both user-facing warnings and platform-side automation.
        """
    )

    st.code(
        """
# Example response shape (illustrative)

{
  "url": "https://example.com",
  "risk_score": 68.2,
  "risk_class": "Suspicious",
  "suggested_action": "Warn",
  "confidence": "HIGH",
  "explanations": [
      "Domain is newly registered",
      "Weak security posture (missing key headers)",
      "Risk indicators align with common scam patterns"
  ]
}
        """,
        language="json",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 7) AUDITABILITY (CRITICAL FOR SERIOUS ADOPTION)
    # -----------------------------------------------------
    st.markdown("### 7) Auditability & Governance (Operational Readiness)")

    st.write(
        """
In real-world deployments, partners often require audit trails for:
incident review, user complaints, false-positive analysis, and continuous tuning.

FraudShield supports an audit-friendly approach by logging:
- timestamp, normalized domain, decision tier, score  
- key signals (non-sensitive)  
- model version + policy version  
This makes decisions reproducible and helps improve accuracy over time.
        """
    )

    st.code(
        """
# Example audit log schema (illustrative)

log_entry = {
  "timestamp": "2025-12-12T18:07:00Z",
  "domain": "example.com",
  "risk_score": 68.2,
  "risk_class": "Suspicious",
  "confidence": "HIGH",
  "model_version": "v1.0",
  "policy_version": "p1.2",
  "signals": {
     "domain_age_days": 41,
     "https_flag": 1,
     "hsts_flag": 0,
     "csp_flag": 0,
     "blacklist_flag": 0
  }
}
        """,
        language="python",
    )

    st.markdown(
        """
This design makes the scoring logic **explainable**, **defensible**, and suitable for
security-sensitive environments where reliability matters.
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





























