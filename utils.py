import requests
from fpdf import FPDF
import time
import pandas as pd

API_URL = "https://website-risk-scorer-api.onrender.com/scan_url"


# ---------------------------------------------------------
# 1) API CALL — Send URL to backend API and return response
# ---------------------------------------------------------
def run_fraudshield_scan(url: str):
    """
    Sends a POST request to the FraudShield API with a URL.
    Returns the API JSON response or None if failed.
    """
    try:
        response = requests.post(API_URL, json={"url": url}, timeout=10)
        return response.json()
    except Exception:
        return None


# ---------------------------------------------------------
# 2) LOGGING — Store scan results into streamlit session log
# ---------------------------------------------------------
def update_log(st_session, url: str, result: str):
    """
    Saves a history entry inside Streamlit session_state.
    """
    if "history" not in st_session:
        st_session["history"] = []

    st_session["history"].append(
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "result": result
        }
    )


# ---------------------------------------------------------
# 3) PDF REPORT — Create a downloadable FraudShield PDF
# ---------------------------------------------------------
def generate_pdf_report(url: str, risk_class: str, risk_score: float):
    """
    Generates a PDF file (in bytes) for downloading via Streamlit.
    """

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "FraudShield Risk Assessment Report", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Website: {url}", ln=True)
    pdf.cell(0, 10, f"Risk Class: {risk_class}", ln=True)
    pdf.cell(0, 10, f"Risk Score: {risk_score:.2f}%", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Analysis Summary:", ln=True)

    pdf.set_font("Arial", size=11)
    pdf.multi_cell(
        0,
        8,
        txt=(
            "This risk score reflects the likelihood that the evaluated website "
            "exhibits characteristics commonly associated with fraudulent or "
            "misleading online environments. Factors considered include domain "
            "trustworthiness, security configuration, traffic signals, metadata "
            "patterns, and threat intelligence sources.\n\n"
            "FraudShield is designed to help prevent exposure to suspicious "
            "websites before harm occurs, offering protective value for users "
            "navigating online shopping environments."
        ),
    )

    # Return PDF as bytes
    return pdf.output(dest="S").encode("latin-1")


# ---------------------------------------------------------
# 4) TABULAR EXAMPLE DATA (Optional helper)
# ---------------------------------------------------------
def get_example_website_table():
    """
    Returns a pandas DataFrame containing sample evaluation results.
    """
    return pd.DataFrame(
        [
            ["amazon.com", "Safe"],
            ["ebay.com", "Low Risk"],
            ["cheapshop247.net", "High Risk"],
            ["brand-outlet-deals.biz", "Suspicious"],
            ["newtechstore.xyz", "High Risk"],
        ],
        columns=["Website", "Risk Result"]
    )
