import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("🧠 Model Intelligence")

st.subheader("Performance Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "95%")
col2.metric("AUC", "0.805")
col3.metric("F1 Score", "0.91")

st.markdown("---")

st.subheader("Feature Importance")
importance = pd.DataFrame({
    "Feature": ["Domain Age", "SSL", "Threatlist", "Keywords", "Hosting"],
    "Importance": [0.31, 0.24, 0.18, 0.12, 0.07]
})
st.bar_chart(importance.set_index("Feature"))

st.markdown("---")

st.subheader("Model Architecture (Simplified)")
st.write("""
