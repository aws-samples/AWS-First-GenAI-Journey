"""Streamlit app for GenAI/Bedrock cost optimization analysis."""

import streamlit as st
import pandas as pd
from router import estimate_savings, MODEL_COSTS

st.set_page_config(page_title="GenAI Cost Optimizer", page_icon="💰")
st.title("💰 AWS GenAI Cost Optimizer")
st.markdown("Upload your Bedrock usage logs to analyze costs and get optimization recommendations.")

st.sidebar.header("Model Pricing (per 1K tokens)")
for model, costs in MODEL_COSTS.items():
    st.sidebar.markdown(f"**{model.title()}**: ${costs['input']} in / ${costs['output']} out")

uploaded_file = st.file_uploader("Upload usage log (CSV)", type=["csv"],
                                  help="CSV with columns: query, model, input_tokens, output_tokens")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    required_cols = {"query", "model", "input_tokens", "output_tokens"}

    if not required_cols.issubset(df.columns):
        st.error(f"CSV must contain columns: {required_cols}")
    else:
        st.subheader("📊 Usage Summary")
        st.write(f"Total queries: **{len(df)}**")
        st.write(f"Models used: **{', '.join(df['model'].unique())}**")

        rows = df.to_dict("records")
        results = estimate_savings(rows)
        results_df = pd.DataFrame(results)

        total_original = results_df["original_cost"].sum()
        total_optimized = results_df["optimized_cost"].sum()
        total_savings = results_df["savings"].sum()
        pct_savings = (total_savings / total_original * 100) if total_original > 0 else 0

        st.subheader("💡 Savings Estimate")
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Cost", f"${total_original:.4f}")
        col2.metric("Optimized Cost", f"${total_optimized:.4f}")
        col3.metric("Savings", f"${total_savings:.4f}", f"{pct_savings:.1f}%")

        st.subheader("🔀 Routing Recommendations")
        complexity_counts = results_df["complexity"].value_counts()
        st.bar_chart(complexity_counts)

        st.subheader("📋 Detailed Results")
        st.dataframe(results_df[["query", "original_model", "recommended_model",
                                  "complexity", "original_cost", "optimized_cost", "savings"]],
                     use_container_width=True)

        st.download_button("Download Results CSV", results_df.to_csv(index=False),
                           "optimization_results.csv", "text/csv")
else:
    st.info("👆 Upload a CSV file to get started. Expected columns: query, model, input_tokens, output_tokens")
    st.markdown("### Sample CSV format")
    st.code("query,model,input_tokens,output_tokens\n"
            "\"What is EC2?\",opus,20,50\n"
            "\"Compare all AWS compute services in detail\",opus,150,500")
