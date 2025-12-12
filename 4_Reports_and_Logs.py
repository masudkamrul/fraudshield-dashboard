import streamlit as st
import pandas as pd
from utils import update_log

st.title("📊 Reports & Logs")

if "history" not in st.session_state:
    st.session_state["history"] = []

st.write("All scans during this session:")

if st.session_state["history"]:
    df = pd.DataFrame(st.session_state["history"])
    st.dataframe(df)

    st.download_button(
        label="⬇ Download Log as CSV",
        data=df.to_csv(index=False),
        file_name="fraudshield_logs.csv",
        mime="text/csv"
    )
else:
    st.info("No logs yet.")

