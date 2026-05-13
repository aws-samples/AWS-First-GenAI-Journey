import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from metrics import fetch_metrics, calculate_costs

st.set_page_config(page_title="GenAI Observability Dashboard", layout="wide")
st.title("🔍 GenAI Observability Dashboard")
st.caption("Monitor token usage, latency, cost, and guardrail blocks")

days = st.sidebar.slider("Days of data", 7, 30, 7)
df = fetch_metrics(days)
costs_df = calculate_costs(df)

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Input Tokens", f"{df['input_tokens'].sum():,}")
col2.metric("Total Output Tokens", f"{df['output_tokens'].sum():,}")
col3.metric("Avg Latency P50", f"{df['latency_p50'].mean():.2f}s")
col4.metric("Total Cost", f"${costs_df['cost'].sum():.2f}")

# Tokens per day chart
st.subheader("📊 Tokens per Day")
fig_tokens = go.Figure()
fig_tokens.add_trace(go.Bar(x=df["date"], y=df["input_tokens"], name="Input Tokens"))
fig_tokens.add_trace(go.Bar(x=df["date"], y=df["output_tokens"], name="Output Tokens"))
fig_tokens.update_layout(barmode="stack", height=300)
st.plotly_chart(fig_tokens, use_container_width=True)

# Latency chart
st.subheader("⏱️ Latency P50 / P99")
fig_latency = go.Figure()
fig_latency.add_trace(go.Scatter(x=df["date"], y=df["latency_p50"], name="P50", mode="lines+markers"))
fig_latency.add_trace(go.Scatter(x=df["date"], y=df["latency_p99"], name="P99", mode="lines+markers"))
fig_latency.update_layout(yaxis_title="Seconds", height=300)
st.plotly_chart(fig_latency, use_container_width=True)

# Cost breakdown and guardrail charts side by side
left, right = st.columns(2)

with left:
    st.subheader("💰 Cost Breakdown by Model")
    fig_cost = px.pie(costs_df, values="cost", names="model", hole=0.4)
    fig_cost.update_layout(height=300)
    st.plotly_chart(fig_cost, use_container_width=True)

with right:
    st.subheader("🛡️ Guardrail Block Rate")
    df["block_rate"] = df["guardrail_blocked"] / df["guardrail_total"] * 100
    fig_guard = px.bar(df, x="date", y="block_rate", labels={"block_rate": "Block Rate (%)"})
    fig_guard.update_layout(height=300)
    st.plotly_chart(fig_guard, use_container_width=True)
