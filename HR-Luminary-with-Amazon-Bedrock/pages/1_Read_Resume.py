import streamlit as st
import recruitment_lib as glib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler

# Set the page configuration with a title and layout
st.set_page_config(page_title="HR Gen AI Assistant", layout="wide")

# Apply custom CSS for better styling
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
            font-family: Arial, sans-serif;
            color: #333333;
        }
        .stApp {
            background-color: #ffffff;
        }
        .title {
            font-size: 2.5em;
            font-weight: bold;
            color: #4A90E2;
            margin-bottom: 20px;
        }
        .description {
            font-size: 1.2em;
            margin-bottom: 40px;
            color: #666666;
        }
        .upload-label {
            font-size: 1.2em;
            font-weight: bold;
            color: #4A90E2;
        }
        .extracted-text {
            background-color: #eeeeee;
            padding: 10px;
            border-radius: 5px;
            margin-top: 20px;
            color: #333333;
            font-family: "Courier New", Courier, monospace;
            white-space: pre-wrap;  /* Preserve whitespace and line breaks */
        }
        .footer {
            font-size: 0.9em;
            color: #aaaaaa;
            margin-top: 50px;
        }
        .button-container {
            margin-top: 20px;
        }
        .btn {
            background-color: #4A90E2;
            color: white;
            padding: 10px 20px;
            font-size: 1em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }
        .btn:hover {
            background-color: #357ABD;
        }
    </style>
""", unsafe_allow_html=True)

# Add a title and description for the app
st.markdown("<div class='title'>HR Gen AI Assistant</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='description'>
        Upload your resume in PDF format to extract and analyze the text content.
        This tool helps in reviewing and improving your resume for job applications.
    </div>
""", unsafe_allow_html=True)

# File uploader for PDF resume
st.markdown("<div class='upload-label'>Upload your resume PDF</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"])
docs = []

if uploaded_file is not None:
    st_callback = StreamlitCallbackHandler(st.container())
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        docs.append(page.extract_text())

    # Display the extracted text from the resume
    st.markdown("<div class='title'>Extracted Text:</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='extracted-text'>{''.join(docs)}</div>", unsafe_allow_html=True)

    # Buttons for submission and interaction
    st.markdown("""
        <div class='button-container'>
            <button class='btn' onclick="window.location.href='/submit'">Submit</button>
            <button class='btn' onclick="window.location.href='/reset'">Reset</button>
        </div>
    """, unsafe_allow_html=True)

# Add a footer
st.markdown("""
    <div class='footer'>
        &copy; 2024 HR Gen AI Assistant. All rights reserved.
    </div>
""", unsafe_allow_html=True)
