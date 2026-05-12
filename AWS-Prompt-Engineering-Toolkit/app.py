"""Streamlit app for testing and comparing prompts across Bedrock models."""

import re
import streamlit as st
import pandas as pd
from evaluator import compare_models

AVAILABLE_MODELS = [
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0",
    "meta.llama3-70b-instruct-v1:0",
]

st.set_page_config(page_title="Prompt Engineering Toolkit", layout="wide")
st.title("🧪 AWS Prompt Engineering Toolkit")
st.caption("Compare prompts across multiple Bedrock models side by side")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    selected_models = st.multiselect("Select models", AVAILABLE_MODELS, default=AVAILABLE_MODELS[:2])
    max_tokens = st.slider("Max tokens", 64, 4096, 1024)

# Prompt template input
st.subheader("Prompt Template")
st.markdown("Use `{{variable}}` syntax for template variables.")
template = st.text_area(
    "Enter your prompt template",
    value="Explain {{topic}} in {{style}} style for a {{audience}} audience.",
    height=120,
)

# Extract and fill variables
variables = re.findall(r"\{\{(\w+)\}\}", template)
var_values = {}
if variables:
    st.subheader("Template Variables")
    cols = st.columns(min(len(variables), 3))
    for i, var in enumerate(variables):
        with cols[i % len(cols)]:
            var_values[var] = st.text_input(f"{var}", key=f"var_{var}")

# Build final prompt
final_prompt = template
for var, val in var_values.items():
    final_prompt = final_prompt.replace(f"{{{{{var}}}}}", val)

with st.expander("Preview resolved prompt"):
    st.code(final_prompt, language=None)

# Run comparison
if st.button("🚀 Run Comparison", type="primary", disabled=not selected_models):
    if not all(var_values.values()):
        st.warning("Please fill in all template variables.")
    else:
        with st.spinner("Running models..."):
            results = compare_models(selected_models, final_prompt, max_tokens)

        # Metrics table
        st.subheader("📊 Metrics Comparison")
        metrics_df = pd.DataFrame(results)[["model_id", "latency_s", "input_tokens", "output_tokens"]]
        metrics_df["total_tokens"] = metrics_df["input_tokens"] + metrics_df["output_tokens"]
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        # Side-by-side outputs
        st.subheader("📝 Model Outputs")
        cols = st.columns(len(results))
        for i, result in enumerate(results):
            with cols[i]:
                model_short = result["model_id"].split(".")[1] if "." in result["model_id"] else result["model_id"]
                st.markdown(f"**{model_short}**")
                st.metric("Latency", f"{result['latency_s']}s")
                st.metric("Tokens", f"{result['input_tokens']}→{result['output_tokens']}")
                st.text_area("Output", result["output"], height=300, key=f"out_{i}", disabled=True)

        # Quality comparison
        st.subheader("⚖️ Quick Quality Check")
        lengths = {r["model_id"].split(".")[-1]: len(r["output"]) for r in results if not r["output"].startswith("ERROR")}
        if lengths:
            st.bar_chart(pd.Series(lengths, name="Response Length (chars)"))
