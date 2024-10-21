import streamlit as st
import recruitment_lib as glib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler

# Set the page configuration with a title
st.set_page_config(page_title="HR Gen AI Assistant", layout="centered")

# Apply custom CSS
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
            border-radius: 4px;
        }
        .stButton button:hover {
            background-color: white;
            color: #4CAF50;
            border: 2px solid #4CAF50;
        }
        .stFileUploader {
            border: 2px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background-color: #fff;
        }
        .stFileUploader:hover {
            border-color: #4CAF50;
        }
        .stTextInput, .stTextarea {
            border: 2px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background-color: #fff;
        }
        .stTextInput:focus, .stTextarea:focus {
            border-color: #4CAF50;
        }
        h1 {
            color: #4CAF50;
            font-size: 36px;
            margin-bottom: 20px;
        }
        .container {
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            background-color: #fff;
            padding: 20px;
            max-width: 700px;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Title and instruction
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.title("HR Gen AI Assistant")
st.write("Upload your resume PDF to get a detailed summary. Ensure the document is in PDF format.")

# File uploader
uploaded_file = st.file_uploader("Upload your resume PDF", type="pdf", help="Choose a PDF file from your device")

# List to hold document texts
docs = []

# If a file is uploaded
if uploaded_file is not None:
    # Create a callback handler for Streamlit
    st_callback = StreamlitCallbackHandler(st.container())
    
    # Read and extract text from each page of the PDF
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        docs.append(page.extract_text())
    
    # Get the summary response
    response = glib.summary_resume_stream(docs, st_callback)
    
    # Display the response
    st.write("### Summary of Your Resume")
    st.write(response)

st.markdown("</div>", unsafe_allow_html=True)
