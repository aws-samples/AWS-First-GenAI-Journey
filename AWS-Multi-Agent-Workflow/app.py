"""Streamlit UI for the Multi-Agent Content Pipeline."""

import streamlit as st
from agents import run_pipeline

st.set_page_config(page_title="Multi-Agent Pipeline", page_icon="🤖")
st.title("🤖 Multi-Agent Content Pipeline")
st.markdown("**Researcher → Writer → Reviewer** using Strands agent-as-tool pattern")

topic = st.text_input("Enter a topic:", placeholder="e.g., Quantum Computing in 2026")

if st.button("Run Pipeline", disabled=not topic):
    with st.spinner("Running multi-agent pipeline..."):
        results = run_pipeline(topic)

    st.subheader("📚 Research Output")
    st.markdown(results["research"])

    st.divider()

    st.subheader("✍️ Writer Output")
    st.markdown(results["article"])

    st.divider()

    st.subheader("✅ Reviewer Output")
    st.markdown(results["review"])
