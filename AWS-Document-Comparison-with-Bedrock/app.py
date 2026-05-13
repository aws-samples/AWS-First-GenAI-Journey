import streamlit as st
from comparator import extract_text, compare_documents

st.set_page_config(page_title="Document Comparison with Bedrock", layout="wide")
st.title("📄 Document Comparison with Amazon Bedrock")
st.write("Upload two PDF documents to compare and highlight key differences using GenAI.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Document 1")
    file1 = st.file_uploader("Upload first PDF", type="pdf", key="pdf1")

with col2:
    st.subheader("Document 2")
    file2 = st.file_uploader("Upload second PDF", type="pdf", key="pdf2")

if file1 and file2:
    text1 = extract_text(file1)
    text2 = extract_text(file2)

    # Show side-by-side document text
    with st.expander("📖 Extracted Text", expanded=False):
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            st.text_area("Document 1 Text", text1, height=300)
        with tcol2:
            st.text_area("Document 2 Text", text2, height=300)

    if st.button("🔍 Compare Documents", type="primary"):
        with st.spinner("Analyzing differences with Amazon Bedrock..."):
            result = compare_documents(text1, text2)
        st.subheader("📋 Comparison Results")
        st.markdown(result)
