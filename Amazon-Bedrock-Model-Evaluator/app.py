import streamlit as st
from pathlib import Path
import os
import boto3
from dotenv import load_dotenv
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Advanced GenAI Model Evaluator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Custom header styling */
        .custom-header {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            border-left: 5px solid #ff4b4b;
        }
        
        /* Card styling */
        .stCard {
            border: 1px solid #e0e0e0;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .stCard:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* File uploader styling */
        .uploadedFile {
            background-color: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        /* Metric card styling */
        .metric-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #ff4b4b;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

def load_env_config():
    """Load and configure environment settings"""
    load_dotenv()
    current_directory = os.getcwd()
    default_region_name = boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else 'us-east-1'
    boto3.setup_default_session()
    current_profile_name = boto3.DEFAULT_SESSION.profile_name

    config = {
        'save_folder': os.getenv('save_folder', current_directory),
        'profile_name': os.getenv('profile_name', current_profile_name),
        'region_name': os.getenv('region_name', 'us-east-1'),
        'max_tokens': int(os.getenv('max_tokens', '4096'))
    }
    
    return config

def display_header():
    """Display the application header with stats"""
    st.markdown("""
        <div class="custom-header">
            <h1>🧠 Advanced GenAI Model Evaluator</h1>
            <p>Evaluate and compare multiple AI models with advanced metrics and visualizations</p>
        </div>
    """, unsafe_allow_html=True)

def file_uploader_section():
    """Enhanced file upload section"""
    st.subheader("📁 Document Upload")
    
    upload_col, info_col = st.columns([2, 1])
    
    with upload_col:
        file = st.file_uploader(
            'Drop your PDF here or click to upload',
            type=["pdf"],
            key="pdf_uploader",
            help="Upload a PDF document for analysis (max 200MB)"
        )
        
        if file:
            file_stats = {
                "File Name": file.name,
                "File Size": f"{round(file.size / 1024 / 1024, 2)} MB",
                "Upload Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            st.markdown("""
                <div class="uploadedFile">
                    <h4>📎 File Uploaded Successfully</h4>
                </div>
            """, unsafe_allow_html=True)
            
            st.json(file_stats)
    
    with info_col:
        st.info("""
        **Supported Formats**
        - PDF documents only
        - Maximum file size: 200MB
        - Text should be extractable
        """)
    
    return file

def model_selection_section():
    """Enhanced model selection interface"""
    st.subheader("🤖 Model Selection")
    
    model_categories = {
        "🌟 Premium Models": {
            "Anthropic": [
                'anthropic.claude-sonnet-4-6',
                'anthropic.claude-haiku-4-5-20251001-v1:0',
                'anthropic.claude-3-haiku-20240307-v1:0',
                'anthropic.claude-3-sonnet-20240229-v1:0',
                'anthropic.claude-v2:1'
            ],
            "Mistral": [
                'mistral.mistral-large-2402-v1:0',
                'mistral.mixtral-8x7b-instruct-v0:1'
            ]
        },
        "⚡ Standard Models": {
            "Meta": [
                'meta.llama3-70b-instruct-v1:0',
                'meta.llama3-8b-instruct-v1:0'
            ],
            "Amazon": [
                'amazon.titan-text-express-v1',
                'amazon.titan-text-lite-v1'
            ]
        }
    }
    
    selected_models = []
    
    for category, providers in model_categories.items():
        st.markdown(f"### {category}")
        cols = st.columns(len(providers))
        
        for col, (provider, models) in zip(cols, providers.items()):
            with col:
                st.markdown(f"**{provider}**")
                selected = st.multiselect(
                    'Choose models',
                    models,
                    key=f"{provider}_models",
                    help=f"Select one or more {provider} models"
                )
                selected_models.extend(selected)
    
    return selected_models

def task_configuration_section(max_tokens):
    """Enhanced task configuration interface"""
    st.subheader("⚙️ Task Configuration")
    
    config_col1, config_col2 = st.columns([2, 1])
    
    with config_col1:
        prompt = st.text_area(
            "Evaluation Prompt",
            "Summarize this document in 2 sentences. Focus on the main points and key findings.",
            help="Enter instructions for the AI models",
            height=100
        )
        
        advanced_options = st.expander("🛠️ Advanced Options")
        with advanced_options:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
            max_length = st.number_input("Maximum Length", 100, max_tokens, 1000)
    
    with config_col2:
        st.markdown("""
        ### Quick Tips
        - Be specific in your instructions
        - Include desired format
        - Specify any constraints
        - Consider the audience
        """)
    
    return {
        "prompt": prompt,
        "temperature": temperature,
        "max_length": max_length
    }

def display_results_section(models, file):
    """Enhanced results display section"""
    st.subheader("📊 Evaluation Results")
    
    # Create tabs for different result views
    overview_tab, details_tab, compare_tab = st.tabs([
        "📈 Overview",
        "📋 Detailed Results",
        "🔄 Model Comparison"
    ])
    
    with overview_tab:
        st.markdown("### Performance Summary")
        metrics_cols = st.columns(3)
        
        # Simulate metrics (replace with actual data)
        with metrics_cols[0]:
            st.metric("Average Response Time", "1.2s", "↓ 0.3s")
        with metrics_cols[1]:
            st.metric("Average Token Usage", "512", "↑ 48")
        with metrics_cols[2]:
            st.metric("Cost per 1K tokens", "$0.002", "↓ $0.001")
    
    with details_tab:
        for model in models:
            with st.expander(f"📑 {model}"):
                st.json({
                    "model": model,
                    "response_time": "1.2s",
                    "tokens_used": 512,
                    "cost": "$0.002"
                })
    
    with compare_tab:
        st.markdown("### Model Comparison")
        st.bar_chart({"Model A": [1, 2, 3], "Model B": [2, 4, 6]})

def model_evaluator():
    """Main evaluation interface"""
    # Load configuration
    config = load_env_config()
    
    # Display header
    display_header()
    
    # Create main tabs
    main_tab, help_tab = st.tabs(["🔍 Evaluation", "❓ Help"])
    
    with main_tab:
        # File upload section
        file = file_uploader_section()
        
        st.markdown("---")
        
        # Model selection section
        selected_models = model_selection_section()
        
        st.markdown("---")
        
        # Task configuration section
        task_config = task_configuration_section(config['max_tokens'])
        
        st.markdown("---")
        
        # Evaluation button and progress
        eval_col1, eval_col2 = st.columns([3, 1])
        
        with eval_col1:
            evaluate_button = st.button(
                "🚀 Start Evaluation",
                use_container_width=True,
                help="Click to begin the evaluation process"
            )
        
        with eval_col2:
            st.metric("Selected Models", len(selected_models))
        
        # Handle evaluation
        if evaluate_button:
            if not file:
                st.warning("⚠️ Please upload a PDF file first")
            elif not selected_models:
                st.warning("⚠️ Please select at least one model")
            elif len(task_config["prompt"]) / 2.5 > config['max_tokens']:
                st.error(f"⚠️ Prompt exceeds maximum token limit of {config['max_tokens']}")
            else:
                with st.spinner("🔄 Processing your request..."):
                    # Save file
                    save_path = Path(config['save_folder'], file.name)
                    with open(save_path, mode='wb') as w:
                        w.write(file.getvalue())
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate processing
                    for i in range(len(selected_models)):
                        progress = (i + 1) / len(selected_models)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing model {i + 1} of {len(selected_models)}...")
                        time.sleep(1)  # Simulate processing time
                    
                    st.success("✅ Evaluation Complete!")
                    
                    # Display results
                    display_results_section(selected_models, file)
    
    with help_tab:
        st.markdown("""
        # 📚 User Guide
        
        ### Getting Started
        1. **Upload Your Document**
           - Supported format: PDF
           - Maximum size: 200MB
           - Ensure text is extractable
        
        ### Selecting Models
        - Choose from different categories
        - Compare multiple models
        - Consider cost vs. performance
        
        ### Configuring Tasks
        - Write clear instructions
        - Set appropriate parameters
        - Monitor token usage
        
        ### Understanding Results
        - Review performance metrics
        - Compare model outputs
        - Analyze cost efficiency
        
        ### Best Practices
        - Use consistent prompts
        - Test with various documents
        - Monitor resource usage
        """)

def rag_evaluator():
    """RAG evaluation interface"""
    st.markdown("## 🚧 Coming Soon")
    st.info("The RAG Evaluator feature is under development. Stay tuned for updates!")

# Sidebar configuration
def configure_sidebar():
    """Configure the sidebar with navigation and branding"""
    with st.sidebar:
        st.image("https://place-hold.it/300x100?text=GenAI%20Evaluator&fontsize=23", use_column_width=True)
        st.markdown("---")
        
        # Navigation
        page_names_to_funcs = {
            "🔍 Model Evaluator": model_evaluator,
            "📚 RAG Evaluator": rag_evaluator
        }
        
        selected_page = st.radio("Select Evaluation Type", page_names_to_funcs.keys())
        
        st.markdown("---")
        
        # Additional sidebar content
        with st.expander("📈 Session Stats"):
            st.markdown("""
                - **Runtime**: Python 3.8+
                - **Framework**: Streamlit 1.2+
                - **Memory Usage**: 512MB
            """)
        
        st.sidebar.info("Made with ❤️ by Your Team")
        
        return page_names_to_funcs[selected_page]

# Main application
if __name__ == "__main__":
    selected_func = configure_sidebar()
    selected_func()