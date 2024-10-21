import streamlit as st
import recruitment_lib as glib
from langchain.callbacks import StreamlitCallbackHandler

# Set the page configuration
st.set_page_config(
    page_title="HR Gen AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
    <style>
        /* Page and text styling */
        .main {
            background-color: #f0f2f6;
            font-family: 'Arial', sans-serif;
        }
        h1 {
            color: #1a73e8;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        h2 {
            color: #1a73e8;
            font-size: 1.5em;
            margin-bottom: 20px;
        }
        .stMarkdown p {
            color: #333333;
            font-size: 1.1em;
        }
        .stTextInput input {
            font-size: 1.1em;
            padding: 10px;
            border: 1px solid #1a73e8;
            border-radius: 5px;
        }
        .stButton button {
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1.1em;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #1664c1;
        }
        .stMarkdown pre {
            background-color: #f1f3f4;
            border: 1px solid #e0e0e0;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize chat history in session state if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("HR Gen AI Assistant")
st.subheader("Ask me anything about recruitment and HR tasks")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

# Sample questions
st.markdown("## Sample Questions:")
st.markdown("- **Viết CV dành cho software developers có 5 năm kinh nghiệm trong lập trình web với ReactJS và .NET Core**")
st.markdown("- **Liệt kê 10 câu hỏi dành cho lập trình viên React**")
st.markdown("- **Top 10 questions for JavaScript**")

# User input text box
input_text = st.text_input("Type your question here...")

# Submit button for user input
if st.button("Submit"):
    if input_text:
        st_callback = StreamlitCallbackHandler(st.container())
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"**You:** {input_text}")
        
        # Append user message to chat history
        st.session_state.chat_history.append({"role": "user", "text": input_text})
        
        # Get and display assistant's response
        chat_response = glib.get_rag_chat_response(input_text, st_callback)
        
        with st.chat_message("assistant"):
            st.markdown(f"**Assistant:** {chat_response}")
        
        # Append assistant's response to chat history
        st.session_state.chat_history.append({"role": "assistant", "text": chat_response})
