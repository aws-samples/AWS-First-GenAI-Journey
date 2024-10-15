import streamlit as st
import Libs as glib
from langchain.callbacks import StreamlitCallbackHandler

# Configure the page
st.set_page_config(page_title="EduChatBot", page_icon="📚", layout="wide")

# Apply custom styling to the page
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        }
        .stTextInput input {
            padding: 10px;
            width: 100%;
            box-sizing: border-box;
        }
    </style>
""", unsafe_allow_html=True)

# Page title and description
st.title("Tìm kiếm kiến thức giáo dục")
st.markdown("### Hỗ trợ tìm kiếm thông tin trong lĩnh vực giáo dục")

# Display sample questions as suggestions
st.markdown("#### Gợi ý câu hỏi:")
col1, col2 = st.columns(2)

# Sample questions linked to backend
sample_questions_col1 = [
    "Những phương pháp học tập hiệu quả?",
    "Làm thế nào để phát triển kỹ năng tư duy phản biện?"
]
sample_questions_col2 = [
    "Các trường đại học hàng đầu thế giới?",
    "Cách lựa chọn ngành học phù hợp?"
]

# Create buttons for each sample question
for question in sample_questions_col1:
    with col1:
        if st.button(question):
            st.session_state.input_text = question

for question in sample_questions_col2:
    with col2:
        if st.button(question):
            st.session_state.input_text = question

# User input field for custom questions
st.markdown("#### Hoặc nhập câu hỏi của bạn:")
input_text = st.text_input("Nhập câu hỏi của bạn ở đây...", value=st.session_state.get('input_text', ''))

# Process the search and display results from backend
if input_text:
    st_callback = StreamlitCallbackHandler(st.container())
    response = glib.search(input_text, st_callback)
    
    # Display search results
    st.write(f"### Kết quả cho câu hỏi: {input_text}")
    st.write(response.get("result", "Không có kết quả"))
    st.json(response)
