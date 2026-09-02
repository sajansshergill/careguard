"""Streamlit view of audit history + latest eval metrics.

Run:  streamlit run dashboards/metrics_dashboard.py
"""
from __future__ import annotations

import json
import os

import pandas as pd
import streamlit as st

from careguard.storage.audit import read_audit

st.set_page_config(page_title="CareGuard Metrics", page_icon="📊")
st.title("CareGuard — Monitoring")

st.header("Latest evaluation")
if os.path.exists("data/eval_report.json"):
    with open("data/eval_report.json", encoding="utf-8") as f:
        report = json.load(f)
    metrics = report.get("metrics", report)
    cols = st.columns(len(metrics))
    for col, (key, value) in zip(cols, metrics.items(), strict=False):
        col.metric(key, value)
    cases = report.get("cases") or []
    if cases:
        st.subheader("Per-case scores")
        st.dataframe(pd.DataFrame(cases), use_container_width=True)
else:
    st.info("No eval report yet — run `python -m careguard.eval`.")

st.header("Audit trail")
rows = read_audit(limit=200)
df = pd.DataFrame(rows)

if df.empty:
    st.info("No cases processed yet.")
else:
    st.dataframe(df, use_container_width=True)
    st.subheader("Decision mix")
    st.bar_chart(df["final_decision"].value_counts())
    st.subheader("Escalation rate")
    st.metric("Escalated", f"{df['escalated'].mean():.0%}")
