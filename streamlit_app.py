# ---------------------------------------------------------
# SCANNER (Improved Professional UI)
# ---------------------------------------------------------
st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

st.subheader("🔍 Website Risk Scanner")

# Bigger, centered, clean URL box
st.markdown(
    """
    <style>
    .big-input input {
        font-size: 18px !important;
        padding: 14px 16px !important;
        border-radius: 8px !important;
        border: 1.5px solid #cccccc !important;
        height: 55px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

url = st.text_input(
    "",
    placeholder="Enter website URL here…",
    key="url_input",
    help="Example: https://example.com",
)

scan_result = None

# ADD SPACING
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Run Scan", use_container_width=True):
    with st.spinner("Analyzing website…"):
        scan_result = run_fraudshield_scan(url)

    if not scan_result:
        st.error("Unable to connect to FraudShield API.")
    else:

        # ------------------------------
        # CLEAN, UNIFIED RESULT BLOCK
        # ------------------------------
        st.markdown("<h4>Scan Results</h4>", unsafe_allow_html=True)

        risk_class = scan_result.get("risk_class", "Unknown")
        risk_score = float(scan_result.get("risk_score", 0))

        badge_color = (
            "risk-low" if risk_class == "Legitimate" else
            "risk-medium" if risk_class == "Suspicious" else
            "risk-high"
        )

        st.markdown("<div class='fs-card'>", unsafe_allow_html=True)

        # Risk Badge
        st.markdown(
            f"<span class='risk-badge {badge_color}'>{risk_class}</span>",
            unsafe_allow_html=True
        )

        # Gauge Chart
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 40], "color": "#d7f5e9"},
                        {"range": [40, 70], "color": "#fff3cd"},
                        {"range": [70, 100], "color": "#f8d7da"},
                    ],
                },
                title={"text": "Risk Score"}
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary explanation
        st.markdown(
            f"""
            **Summary:**  
            The website **{url}** has been analyzed using FraudShield’s machine-learning system.  
            Based on current indicators, it is classified as **{risk_class}** with a risk score of **{risk_score:.1f}/100**.
            """,
            unsafe_allow_html=True
        )

        # Add small professional indicators (optional)
        st.markdown(
            """
            **Key Indicators Considered:**
            - Domain trust & age  
            - SSL / HTTPS configuration  
            - Known threat intelligence matches  
            - Metadata consistency  
            - Risk patterns of fraudulent stores  
            """,
            unsafe_allow_html=True
        )

        # Log activity
        update_log(st.session_state, url, risk_class)

        # PDF Report
        pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fraudshield_report.pdf",
            mime="application/pdf"
        )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
