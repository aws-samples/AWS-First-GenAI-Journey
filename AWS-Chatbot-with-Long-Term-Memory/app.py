import streamlit as st
import boto3
from memory import save_message, get_history, summarize_history

bedrock = boto3.client("bedrock-runtime")
MODEL_ID = "anthropic.claude-sonnet-4-6"

st.set_page_config(page_title="Chatbot with Memory", page_icon="🧠")
st.title("🧠 Chatbot with Long-Term Memory")

if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# User login
user_id = st.sidebar.text_input("Enter your User ID:", value=st.session_state.user_id)
if user_id and user_id != st.session_state.user_id:
    st.session_state.user_id = user_id
    st.session_state.messages = get_history(user_id)
    st.rerun()

if not st.session_state.user_id:
    st.info("Please enter a User ID in the sidebar to start chatting.")
    st.stop()

# Memory summary
if st.sidebar.button("Show Memory Summary"):
    with st.sidebar:
        with st.spinner("Summarizing..."):
            st.write(summarize_history(st.session_state.user_id))

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"][0]["text"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    user_msg = {"role": "user", "content": [{"text": prompt}]}
    st.session_state.messages.append(user_msg)
    save_message(st.session_state.user_id, "user", prompt)

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = bedrock.converse(
                modelId=MODEL_ID,
                messages=st.session_state.messages,
                system=[{"text": "You are a helpful assistant. Use conversation history for context."}],
            )
            reply = response["output"]["message"]["content"][0]["text"]
            st.write(reply)

    assistant_msg = {"role": "assistant", "content": [{"text": reply}]}
    st.session_state.messages.append(assistant_msg)
    save_message(st.session_state.user_id, "assistant", reply)
