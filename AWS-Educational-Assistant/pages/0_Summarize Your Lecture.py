import streamlit as st
from PyPDF2 import PdfReader
import Libs as glib

# Page configuration
st.set_page_config(page_title="Summarize Your Lecture or Paper", page_icon=":books:", layout="wide")

# Custom CSS for styling with the provided color palette
st.markdown("""
    <style>
        .title {
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #6A9CFD; /* Blue */
        }
        .subtitle {
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #FFB8D0; /* Pink */
            margin-bottom: 40px;
        }
        .upload-box {
            border: 2px dashed #FEE5E1; /* Soft Pink */
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            background-color: #FFFBF3; /* Very Light Pink */
        }
        .response-box {
            background-color: #AEE4FF; /* Light Blue */
            padding: 20px;
            border-radius: 10px;
            text-align: left;
            white-space: pre-wrap;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 1.1em;
            line-height: 1.6;
            color: #FFB8D0; /* Pink */
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #6A9CFD; /* Blue */
            margin-top: 40px;
            font-size: 0.9em;
        }
        .stButton>button {
            background-color: #FFB8D0; /* Pink */
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# Page title and description
st.markdown('<h1 class="title">Summarize Your Lecture or Paper</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a PDF document and let our AI-powered tool generate a concise summary for you.</p>', unsafe_allow_html=True)

# PDF upload box
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Your PDF Document", type="pdf")
st.markdown('</div>', unsafe_allow_html=True)

docs = []

# Process the uploaded file
if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                docs.append(text)
            else:
                st.warning("A page could not be read and has been skipped.")
        
        # Show a loading spinner while processing
        with st.spinner('Generating summary...'):
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            summary = ""
            for chunk in glib.summary_stream(docs):
                if chunk:
                    summary += chunk + " "
            st.markdown(summary, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
else:
    st.info("Please upload a PDF document to start the summarization process.")

# Footer
st.markdown('<div class="footer">Powered by Streamlit and AI</div>', unsafe_allow_html=True)
