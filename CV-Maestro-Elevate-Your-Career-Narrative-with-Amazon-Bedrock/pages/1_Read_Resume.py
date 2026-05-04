# app.py
import streamlit as st
import boto3
from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.callbacks import StreamlitCallbackHandler
import recruitment_lib as glib
from typing import List, Optional
import json

# Constants and configurations
CLAUDE_MODEL = "anthropic.claude-sonnet-4-6"

class BedrockClient:
    def __init__(self):
        self.client = boto3.client('bedrock-runtime')
    
    def generate_analysis(self, text: str) -> str:
        try:
            # Correct format for Claude 3.5 on Bedrock
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Please analyze this resume and provide detailed feedback on structure, content, formatting, and areas for improvement:\n\n{text}"
                    }
                ],
                "temperature": 0.7
            })
            
            response = self.client.invoke_model(
                modelId=CLAUDE_MODEL,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('content', [{}])[0].get('text', '')
            
        except Exception as e:
            st.error(f"Error generating analysis: {str(e)}")
            return ""

class ResumeProcessor:
    @staticmethod
    def extract_text_from_pdf(file) -> List[str]:
        try:
            reader = PdfReader(file)
            return [page.extract_text() for page in reader.pages]
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return []

class UI:
    def __init__(self):
        self.setup_page_config()
        self.load_css()
        self.bedrock_client = BedrockClient()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="HR GenAI Assistant",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def load_css(self):
        st.markdown("""
            <style>
                /* Modern color scheme */
                :root {
                    --primary-color: #2E86C1;
                    --secondary-color: #3498DB;
                    --background-color: #F8F9FA;
                    --text-color: #2C3E50;
                }
                
                .stApp {
                    background-color: var(--background-color);
                }
                
                /* Header styling */
                .header-container {
                    padding: 2rem;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                }
                
                .app-title {
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                }
                
                .app-description {
                    font-size: 1.1rem;
                    color: var(--text-color);
                    line-height: 1.6;
                }
                
                /* Content containers */
                .content-container {
                    background-color: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 1.5rem;
                }
                
                /* Analysis section */
                .analysis-container {
                    background-color: #F7F9FC;
                    padding: 1.5rem;
                    border-radius: 8px;
                    border-left: 4px solid var(--primary-color);
                }
                
                /* Buttons */
                .stButton>button {
                    background-color: var(--primary-color);
                    color: white;
                    border-radius: 5px;
                    padding: 0.5rem 1rem;
                    font-weight: 500;
                    border: none;
                    transition: all 0.3s ease;
                }
                
                .stButton>button:hover {
                    background-color: var(--secondary-color);
                    transform: translateY(-2px);
                }
                
                /* File uploader */
                .uploadedFile {
                    border: 2px dashed var(--primary-color);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 1rem 0;
                }
                
                /* Progress indicators */
                .stProgress {
                    height: 6px;
                    background-color: var(--primary-color);
                }
                
                /* Analysis results */
                .results-section {
                    margin-top: 2rem;
                    padding: 1.5rem;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .results-section h3 {
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                }
            </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        st.markdown("""
            <div class="header-container">
                <div class="app-title">HR GenAI Assistant</div>
                <div class="app-description">
                    Upload your resume for AI-powered analysis using Claude 3.5. 
                    Get comprehensive feedback on your resume's content, structure, and presentation.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### About")
            st.info("""
                This application uses Claude 3.5 on AWS Bedrock to analyze resumes 
                and provide professional feedback. Simply upload your PDF resume 
                to get started.
            """)
            
            st.markdown("### Tips")
            st.success("""
                - Upload a clean PDF version of your resume
                - Make sure text is selectable (not scanned)
                - Wait a few seconds for the analysis
                - Review both the extracted text and AI feedback
            """)
    
    def render_main_content(self):
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF format)",
            type=["pdf"],
            help="Please ensure your resume is in PDF format with selectable text"
        )
        
        if uploaded_file:
            with st.spinner("Processing your resume..."):
                docs = ResumeProcessor.extract_text_from_pdf(uploaded_file)
                
                if docs:
                    with st.expander("📄 View Extracted Text", expanded=False):
                        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
                        st.text(''.join(docs))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🔍 Analyze Resume", use_container_width=True):
                            with st.spinner("Generating comprehensive analysis..."):
                                analysis = self.bedrock_client.generate_analysis(''.join(docs))
                                
                                if analysis:
                                    st.markdown('<div class="results-section">', unsafe_allow_html=True)
                                    st.markdown("### 📊 AI Analysis Results")
                                    st.markdown(analysis)
                                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        self.render_header()
        self.render_sidebar()
        self.render_main_content()

if __name__ == "__main__":
    app = UI()
    app.run()