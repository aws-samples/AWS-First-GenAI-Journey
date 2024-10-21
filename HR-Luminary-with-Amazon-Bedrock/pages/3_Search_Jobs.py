import streamlit as st 
import recruitment_lib as glib 
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler

def print_result(st, response):
    try:
        st.dataframe(response['intermediate_steps'][1][1])
        st.subheader("Conclusion:")
        st.write(response['output'])
    except:
        st.write(response['output'])

# Set the page configuration
st.set_page_config(page_title="Job Search App", page_icon=":mag:", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextInput>div>div>input {
            border: 2px solid #ccc;
            border-radius: 4px;
            padding: 10px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }
        .stTextInput>div>div>input:focus {
            border-color: #4CAF50;
        }
        .stMarkdown, .stTextInput, .stButton, .stSubheader, .stTitle {
            margin-bottom: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Title and Introduction
st.title("Welcome to the Job Search App")
st.subheader("Find your ideal job position with ease")
st.markdown("Enter the job position you are looking for and let us help you find the best matches available.")

# Input Field
input_text = st.text_input("Enter the job position you are looking for:")

# Search Button
search_button = st.button("Search")

# If input is provided and search button is clicked
if input_text and search_button: 
    st_callback = StreamlitCallbackHandler(st.container())
    response = glib.search_jobs(input_text, st_callback)
    print_result(st, response)
