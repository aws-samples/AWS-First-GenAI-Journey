import streamlit as st
import Libs as glib
from PyPDF2 import PdfReader

# Configure the page
st.set_page_config(
    page_title="Education Document Q&A",
    page_icon=":books:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling with colors from your palette
st.markdown("""
    <style>
        .main { 
            background-color: #FFFFFF; /* White background */
            padding: 20px;
            border-radius: 10px;
        }
        .header {
            text-align: center;
            color: #6A9CFD; /* Blue */
            font-size: 3em;
            font-weight: bold;
        }
        .subheader {
            text-align: center;
            color: #FFB8D0; /* Pink */
            font-size: 1.5em;
        }
        .footer {
            text-align: center;
            color: #FFBFB3; /* Light Coral */
            font-size: 0.9em;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        .stButton>button {
            color: white;
            background-color: #6A9CFD; /* Blue */
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1em;
        }
        .file-uploader {
            margin-top: 20px;
        }
        .question-input {
            margin-top: 20px;
        }
        .sample-questions {
            margin-top: 20px;
            font-size: 1.2em;
        }
        .question-input input {
            border-radius: 5px;
            padding: 10px;
            width: 100%;
            background-color: #FEE5E1; /* Light Pink */
        }
    </style>
""", unsafe_allow_html=True)

# Header and Introduction
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.markdown("<h1 class='header'>Education Document Q&A</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Upload your educational document in PDF format and ask any questions about the content!</p>", unsafe_allow_html=True)

# File uploader for PDF
uploaded_file = st.file_uploader("Upload Your Document in PDF", type="pdf", help="Please upload your document in PDF format.")

# Sample questions section
st.markdown("<div class='sample-questions'><strong>Sample Questions:</strong></div>", unsafe_allow_html=True)
st.markdown("<ul class='sample-questions'><li>Summarize the document</li><li>What are the main points of the document?</li><li>Explain the key concepts discussed</li></ul>", unsafe_allow_html=True)

# User question input
input_text = st.text_input("Your question:", placeholder="Type your question here...")

# Additional action buttons
st.markdown("""
    <div class="button-container">
        <button onclick="document.getElementById('input').value='Summarize the document'">Summarize</button>
        <button onclick="document.getElementById('input').value='What are the main points of the document?'">Main Points</button>
        <button onclick="document.getElementById('input').value='Explain the key concepts discussed'">Key Concepts</button>
    </div>
""", unsafe_allow_html=True)

# Process and display the result if a file is uploaded and a question is asked
docs = []
if uploaded_file and input_text:
    if st.button("Submit Question"):
        with st.spinner('Processing your request...'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                docs.append(page.extract_text())
            
            response = glib.query_document(input_text, docs)
            st.success('Here is the answer to your question:')
            st.write(response)

# Add footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p class='footer'>Developed by AWS Vietnam team</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
