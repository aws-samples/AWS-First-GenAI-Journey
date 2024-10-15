import streamlit as st
import Libs as glib

# Configure the Streamlit page
st.set_page_config(page_title="AWS Educational Assistant", layout="wide")

# Custom CSS for the page
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput, .stButton {
        width: 100%;
        margin-bottom: 10px;
    }
    .st-chat-message {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 10px;
    }
    .st-chat-message.user {
        background-color: #d1e7dd;
        text-align: left;
        border: 1px solid #bcd0c7;
    }
    .st-chat-message.bot {
        background-color: #f8d7da;
        text-align: right;
        border: 1px solid #f5c2c7;
    }
    .title {
        font-size: 3em;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 20px;
    }
    .description {
        text-align: center;
        font-size: 1.2em;
        color: #333;
        margin-bottom: 20px;
    }
    .examples {
        margin-bottom: 20px;
    }
    .examples ul {
        list-style-type: none;
        padding: 0;
    }
    .examples li {
        margin: 5px 0;
        padding: 10px;
        background: #fff;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .footer {
        text-align: center;
        font-size: 0.8em;
        color: #aaa;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Page title and description
st.markdown('<div class="title">AWS Educational Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Ask me anything related to AWS and educational topics!</div>', unsafe_allow_html=True)

# Example questions for users to try
st.markdown("""
<div class="examples">
    <p>Here are some examples to get you started:</p>
    <ul>
        <li>What is AWS Lambda, and how does it work?</li>
        <li>Can you explain the benefits of using Amazon S3?</li>
        <li>How to set up a VPC in AWS?</li>
        <li>What are the best practices for securing AWS environments?</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# User input box for questions
input_text = st.text_input("Type your question here", placeholder="Enter your question...")

# Processing the user question and displaying the response
if input_text:
    with st.chat_message("user"):
        st.markdown(f"**You:** {input_text}")
    
    response_placeholder = st.empty()

    response_stream = glib.call_claude_sonet_stream(input_text)
    
    response = ""
    for chunk in response_stream:
        if chunk:
            response += chunk
            response_placeholder.markdown(f"**Bot:** {response}")

    with st.chat_message("bot"):
        st.markdown(f"**Bot:** {response}")

# Footer information
st.markdown('<div class="footer">Developed by AWS Vietnam Team.</div>', unsafe_allow_html=True)
