import streamlit as st
import recruitment_lib as glib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler

# Set up the page configuration
st.set_page_config(page_title="Search Insight Resume", layout="centered", initial_sidebar_state="auto")

# Custom CSS for improved UI
st.markdown("""
    <style>
        /* General settings */
        body {
            font-family: 'Open Sans', sans-serif;
        }

        /* Page title */
        .title {
            color: #2E7D32;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Section title */
        .section-title {
            color: #2E7D32;
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 20px;
        }

        /* File uploader */
        .file-uploader {
            background-color: #e8f5e9;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            padding: 10px;
        }

        /* Text input */
        .text-input {
            border: 1px solid #4CAF50;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 20px;
        }

        /* Response box */
        .response-box {
            background-color: #e8f5e9;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            padding: 10px;
        }

        /* Sample questions */
        .sample-questions {
            color: #424242;
            font-size: 1em;
        }

        /* Sample question item */
        .sample-question-item {
            color: #424242;
            font-size: 1em;
            margin-bottom: 5px;
        }

        /* Submit button */
        .submit-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .submit-button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# Page Title
st.markdown('<div class="title">📄 Search Insight Resume</div>', unsafe_allow_html=True)

# File Uploader
st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])
st.markdown('</div>', unsafe_allow_html=True)
docs = []

# Sample Questions Section
st.markdown('<div class="section-title">Ask me anything about the resume, for example:</div>', unsafe_allow_html=True)
st.markdown('<div class="sample-questions">', unsafe_allow_html=True)
sample_questions = [
    "Does this resume have experience with React.js or Angular?",
    "Does this resume have strong experience in backend development?",
    "Hồ sơ này có nhiều kĩ năng .NET không?",
    "Does this resume have strong experience with AWS?"
]
for question in sample_questions:
    st.markdown(f'<div class="sample-question-item">- {question}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Text Input for the Question
st.markdown('<div class="text-input">', unsafe_allow_html=True)
input_text = st.text_input("🔍 Your question:")
st.markdown('</div>', unsafe_allow_html=True)

# Submit Button
if st.button('Submit', key='submit-button'):
    if uploaded_file is not None and input_text:
        st_callback = StreamlitCallbackHandler(st.container())
        reader = PdfReader(uploaded_file)
        
        # Extract text from each page of the uploaded PDF
        for page in reader.pages:
            docs.append(page.extract_text())
        
        # Query the resume with the input text
        response = glib.query_resume(input_text, docs, st_callback)
        
        # Display the response
        st.markdown('<div class="response-box">', unsafe_allow_html=True)
        st.write(response)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Please upload a resume PDF and enter a question.")
