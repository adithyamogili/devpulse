import os
import pandas as pd
import psycopg
import streamlit as st

st.set_page_config(page_title="DevPulse | Engineering Analytics", page_icon="📈", layout="wide")
st.title("DevPulse — GitHub Engineering Analytics")
st.caption("A cross-repository view of public GitHub engineering activity.")

DB_URL = os.getenv("DATABASE_URL", "postgresql://devpulse:devpulse@postgres:5432/devpulse")

@st.cache_data(ttl=60)
def query(sql):
    with psycopg.connect(DB_URL) as conn:
        return pd.read_sql_query(sql, conn)

try:
    activity = query("select * from gold.mart_repository_activity order by repository_full_name")
    pr = query("select * from gold.mart_pull_request_metrics order by repository_full_name")
    issues = query("select * from gold.mart_issue_metrics order by repository_full_name")
    if activity.empty:
        st.info("No Gold data yet. Run ingestion, wait for Kafka consumer, then run dbt.")
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Repositories", len(activity))
        c2.metric("Commit records", int(activity.commit_records.sum()))
        c3.metric("Pull requests", int(activity.pull_request_records.sum()))
        c4.metric("Issue records", int(activity.issue_records.sum()))
        st.subheader("Repository activity")
        st.dataframe(activity, use_container_width=True, hide_index=True)
        st.subheader("Pull request metrics")
        st.dataframe(pr, use_container_width=True, hide_index=True)
        st.subheader("Issue metrics")
        st.dataframe(issues, use_container_width=True, hide_index=True)
        st.bar_chart(activity.set_index("repository_full_name")[["commit_records","issue_records","pull_request_records"]])
except Exception as exc:
    st.warning("Analytics tables are not available yet. Run ingestion, Spark and dbt first.")
    st.code(str(exc))
