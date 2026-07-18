import streamlit as st
import pandas as pd
import os

import config

st.set_page_config(page_title="EMA Golden Cross Scanner", layout="wide")
st.title("📈 50/200 EMA Golden Cross Scanner (4Hr) — BUY Signals")
st.caption("Scanning GitHub Actions se automatically roz 9:30 AM - 12:00 PM chalti hai.")

if os.path.exists(config.NOTIFIED_LOG_FILE):
    df = pd.read_csv(config.NOTIFIED_LOG_FILE)
    df = df.sort_values("notified_at", ascending=False)

    st.metric("Total signals ab tak", len(df))

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    today_signals = df[df["notified_at"].str.startswith(today)]
    st.subheader(f"Aaj ke signals ({len(today_signals)})")
    st.dataframe(today_signals, use_container_width=True)

    st.subheader("Poora signal history")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Abhi tak koi scan complete nahi hua. Pehle GitHub Actions run hone ka wait karo.")
