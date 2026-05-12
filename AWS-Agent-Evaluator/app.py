"""Streamlit app for evaluating AI agent performance."""
import json
import streamlit as st
from eval_runner import EvalScenario, load_scenarios, run_evaluation

st.set_page_config(page_title="Agent Evaluator", layout="wide")
st.title("🤖 AWS Agent Evaluator")
st.markdown("Evaluate AI agent responses against predefined test scenarios.")

# Load scenarios
try:
    scenarios = load_scenarios()
except FileNotFoundError:
    st.error("scenarios.json not found. Please create it first.")
    st.stop()

# Sidebar - scenario selection
st.sidebar.header("Configuration")
all_tags = sorted({t for s in scenarios for t in s.tags})
selected_tags = st.sidebar.multiselect("Filter by tags", all_tags, default=all_tags)
filtered = [s for s in scenarios if any(t in selected_tags for t in s.tags)]
st.sidebar.metric("Scenarios", len(filtered))

# Main area - run evaluations
st.header("Test Scenarios")

if "results" not in st.session_state:
    st.session_state.results = []

# Input area for agent responses
with st.expander("📝 Enter Agent Responses", expanded=True):
    responses = {}
    for scenario in filtered:
        responses[scenario.name] = st.text_area(
            f"Response for: {scenario.input}",
            key=f"resp_{scenario.name}",
            height=80,
        )

# Run evaluation
if st.button("▶️ Run Evaluation", type="primary"):
    results = []
    for scenario in filtered:
        resp = responses.get(scenario.name, "")
        if resp.strip():
            result = run_evaluation(scenario, resp)
            results.append(result)
    st.session_state.results = results

# Display results
if st.session_state.results:
    st.header("Results")
    results = st.session_state.results
    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    col1, col2, col3 = st.columns(3)
    col1.metric("Pass Rate", f"{passed}/{total}")
    col2.metric("Avg Accuracy", f"{sum(r['accuracy'] for r in results) / total:.1%}")
    col3.metric("Avg Safety", f"{sum(r['safety'] for r in results) / total:.1%}")

    for r in results:
        icon = "✅" if r["passed"] else "❌"
        with st.expander(f"{icon} {r['scenario']} (Overall: {r['overall']:.3f})"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Accuracy", f"{r['accuracy']:.3f}")
            c2.metric("Relevance", f"{r['relevance']:.3f}")
            c3.metric("Safety", f"{r['safety']:.3f}")
