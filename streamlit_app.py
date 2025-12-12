# ----------- RESULT CARD -----------
st.markdown("<div class='fs-card' style='text-align:center;'>", unsafe_allow_html=True)

# Risk Badge Color Logic
if risk_class.lower() in ["legitimate", "safe", "low"]:
    badge_color = "#2ecc71"   # green
    badge_text = "Safe"
elif risk_class.lower() in ["medium", "suspicious", "unknown"]:
    badge_color = "#f1c40f"   # yellow
    badge_text = "Low Risk"
else:
    badge_color = "#e74c3c"   # red
    badge_text = "High Risk"

# Risk Badge (bigger + centered)
st.markdown(
    f"""
    <div style="
        display:inline-block;
        background:{badge_color};
        color:white;
        padding:10px 24px;
        border-radius:22px;
        font-size:20px;
        font-weight:600;
        margin-bottom:10px;
    ">
        {badge_text}
    </div>
    """,
    unsafe_allow_html=True
)

# Gauge Chart (compact spacing)
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=risk_score,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "black"},
            "steps": [
                {"range": [0, 40], "color": "#d4f6e4"},  # green-ish
                {"range": [40, 70], "color": "#fff3cd"}, # yellow-ish
                {"range": [70, 100], "color": "#f8d7da"},# red-ish
            ],
        },
        title={"text": ""}
    )
)

st.plotly_chart(fig, use_container_width=False)

# Summary
st.markdown(
    f"""
    <div style="font-size:16px; margin-top:15px;">
    Website <strong>{url}</strong> was evaluated using FraudShield’s machine-learning system.  
    It is classified as <strong>{badge_text}</strong> with a risk score of <strong>{risk_score:.1f}/100</strong>.
    </div>
    """,
    unsafe_allow_html=True
)

# Key Indicators
st.markdown(
    """
    <br>
    <strong>Key Indicators Considered</strong><br>
    • Domain age & trust signals<br>
    • SSL configuration<br>
    • Threat intelligence matches<br>
    • Metadata structure<br>
    • Fraud-pattern signals<br><br>
    """
)

# PDF Report
pdf_bytes = generate_pdf_report(url, risk_class, risk_score)
st.download_button(
    label="📄 Download PDF Report",
    data=pdf_bytes,
    file_name="fraudshield_report.pdf",
    mime="application/pdf"
)

st.markdown("</div>", unsafe_allow_html=True)
