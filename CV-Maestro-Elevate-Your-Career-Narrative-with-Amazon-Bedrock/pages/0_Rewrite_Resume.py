import streamlit as st
import recruitment_lib as glib
from langchain.callbacks import StreamlitCallbackHandler

# Setting the page configuration with a custom title
st.set_page_config(page_title="HR Gen AI Assistant", page_icon=":robot_face:")

# Custom CSS styles for a professional look
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
            padding: 20px;
            font-family: 'Arial', sans-serif;
        }
        .stTextArea {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            background-color: #fff;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stTitle, .stSubheader {
            color: #333;
        }
        .stMarkdown {
            background-color: #fff;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)

# Displaying a title and subheader to make the page more appealing
st.title("HR Gen AI Assistant")
st.subheader("Get AI-powered assistance with your recruitment process")

# Creating a text area for users to input their resume or a part of it
input_text = st.text_area("Paste your resume or a section of it below:", height=200)

# Adding a button to submit the resume
if st.button("Submit"):
    # Checking if the input is not empty
    if input_text:
        # Initializing the callback handler
        st_callback = StreamlitCallbackHandler(st.container())
        # Calling the resume rewrite function from the library
        chat_response = glib.rewrite_resume(input_text, st_callback)
        
        # Displaying the response in an assistant-styled chat message
        st.markdown(f"<div class='stMarkdown'>{chat_response}</div>", unsafe_allow_html=True)
    else:
        st.warning("Please paste your resume text before submitting.")
        
# Adding an optional button for further assistance or feedback
if st.button("Need more help?"):
    st.markdown("""
        <div class='stMarkdown'>
            If you need more personalized assistance, please contact our support team or visit our help center.
        </div>
    """, unsafe_allow_html=True)
