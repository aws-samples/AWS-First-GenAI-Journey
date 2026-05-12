"""Streamlit UI for the AWS Agentic Assistant."""

import streamlit as st
from agent import create_agent

st.set_page_config(page_title="AWS Agentic Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AWS Agentic Assistant")
st.caption("Powered by Strands Agents SDK + Amazon Bedrock + MCP")

# Initialize agent in session
if "agent" not in st.session_state:
    st.session_state.agent = create_agent(use_mcp=False)
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about AWS services, architecture, or anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.agent(prompt)
            response = str(result)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
