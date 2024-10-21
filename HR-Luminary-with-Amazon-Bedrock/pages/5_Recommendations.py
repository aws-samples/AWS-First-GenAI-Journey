import streamlit as st
import recruitment_lib as glib
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler

def print_result(st, response):
    st.success("Analysis Complete!")
    try:
        with st.expander("Detailed Analysis"):
            st.dataframe(response['intermediate_steps'][1][1])
        st.subheader("Conclusion:")
        st.write(response['output'])
    except:
        st.write(response['output'])

# Set page configuration
st.set_page_config(
    page_title="HR Gen AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .stApp {
        background-color: #f9f9f9;
        color: #333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .stFileUploader {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
    }
    .stTextInput>div>div>input {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🤖 HR Gen AI Assistant")
st.write("Upload your resume in PDF format to get detailed feedback and recommendations.")

# File uploader
uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"], help="Only PDF files are supported.")

# Action buttons
col1, col2, col3 = st.columns(3)
with col1:
    analyze_button = st.button("Analyze Resume")

with col2:
    clear_button = st.button("Clear")

with col3:
    help_button = st.button("Help")

if help_button:
    st.info("Upload a PDF resume and click on 'Analyze Resume' to get started.")

docs = []
agent = glib.initializeAgent()

if uploaded_file is not None and analyze_button:
    st_callback = StreamlitCallbackHandler(st.container())
    reader = PdfReader(uploaded_file)
    
    for page in reader.pages:
        docs.append(page.extract_text())

    response = agent({
            "input": str(docs),
            "output": "output",
            "chat_history": [],
         },
            callbacks=[st_callback])
    
    # Display the result
    print_result(st, response)
elif clear_button:
    st.cache_data.clear()  # Corrected cache clearing method
    st.experimental_rerun()
else:
    st.info("Please upload a PDF file to proceed.")
