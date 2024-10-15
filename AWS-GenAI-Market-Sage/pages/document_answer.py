import streamlit as st 
import libs as glib 
from PyPDF2 import PdfReader
import base

# Set the page configuration
st.set_page_config(page_title="Hỏi đáp về tài liệu", page_icon="img/favicon.ico", layout="wide")

# Custom CSS styling
st.markdown(
  """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button {
            background-color: #f63366;
            color: white;
            border-radius: 5px;
        }
        .custom-title {
            font-size: 2em;
            font-weight: bold;
            color: #f63366;
            margin-bottom: 20px;
        }
        .custom-box {
            background-color: #f1f3f6;
            border-radius: 10px;
            padding: 15px;
            margin-top: 10px;
        }
    </style>
  """, 
  unsafe_allow_html=True
)

# Title
st.markdown('<div class="custom-title">Hỏi đáp về tài liệu</div>', unsafe_allow_html=True)

# Initialize the sidebar and animation (assuming base has these functions)
base.init_slidebar()
base.init_animation()

# PDF Upload Section
uploaded_file = st.file_uploader("Tải tài liệu định dạng PDF để hỏi đáp", type=["pdf"])

# Provide sample questions for users
st.markdown("### Hãy hỏi thông tin về nội dung tài liệu, ví dụ:")
st.markdown("- Tóm tắt nội dung của tài liệu") 
st.markdown("- Nêu những điểm nổi bật của tài liệu")

# Text input for user's question
input_text = st.text_input("Câu hỏi của bạn!")

# Initialize document list
docs = []

# Handle PDF upload and question submission
if uploaded_file is not None:
    # Preview uploaded PDF file (first few pages)
    pdf_preview_expander = st.expander("Xem trước tài liệu")
    with pdf_preview_expander:
        reader = PdfReader(uploaded_file)
        preview_text = ""
        for page_num, page in enumerate(reader.pages[:2]):  # Preview first 2 pages
            preview_text += f"**Trang {page_num + 1}**: {page.extract_text()}\n\n"
        st.markdown(preview_text)

    # Process the document and respond to the user's question
    if input_text:
        for page in reader.pages:
            docs.append(page.extract_text())
        
        with st.spinner('Đang xử lý tài liệu, vui lòng chờ...'):
            response = glib.query_document(input_text, docs)
        
        # Display the response in a styled box
        st.markdown('<div class="custom-box">', unsafe_allow_html=True)
        st.write(response)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer message
st.markdown("<p style='color:gray;text-align:center;'>Powered by AWS</p>", unsafe_allow_html=True)
