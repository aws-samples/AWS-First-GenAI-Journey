"""Multimodal RAG Streamlit app using Amazon Bedrock Knowledge Bases."""

import os
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from rag_engine import RAGConfig, index_document, query


@dataclass
class AppConfig:
    title: str = "Multimodal RAG with Amazon Bedrock"
    supported_types: tuple = ("pdf", "png", "jpg", "jpeg", "mp4", "mov")
    max_file_size_mb: int = 100


def init_config() -> RAGConfig:
    """Initialize RAG config from environment or sidebar inputs."""
    with st.sidebar:
        st.header("Configuration")
        region = st.text_input("AWS Region", value=os.environ.get("AWS_REGION", "us-east-1"))
        kb_id = st.text_input("Knowledge Base ID", value=os.environ.get("BEDROCK_KB_ID", ""))
        s3_bucket = st.text_input("S3 Bucket", value=os.environ.get("S3_BUCKET", ""))
        model_id = st.text_input("Model ID", value=os.environ.get("MODEL_ID", "anthropic.claude-sonnet-4-6"))
    return RAGConfig(region=region, kb_id=kb_id, s3_bucket=s3_bucket, model_id=model_id)


def render_upload_section(config: RAGConfig) -> None:
    """Render file upload and indexing UI."""
    st.subheader("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs, images, or videos",
        type=list(AppConfig.supported_types),
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("Index Documents"):
        for f in uploaded_files:
            with st.spinner(f"Uploading {f.name}..."):
                uri = index_document(f.getvalue(), f.name, config)
                st.success(f"Indexed: {uri}")


def render_query_section(config: RAGConfig) -> None:
    """Render question input and answer display."""
    st.subheader("💬 Ask Questions")
    question = st.text_input("Enter your question about the uploaded documents:")
    if question and st.button("Get Answer"):
        if not config.kb_id:
            st.error("Please configure a Knowledge Base ID.")
            return
        with st.spinner("Retrieving and generating answer..."):
            result = query(question, config)
        st.markdown("### Answer")
        st.write(result["answer"])
        if result["citations"]:
            st.markdown("### Sources")
            for i, cite in enumerate(result["citations"], 1):
                with st.expander(f"Source {i}: {Path(cite['source']).name if cite['source'] else 'N/A'}"):
                    st.text(cite["text"][:500])
                    if cite["source"]:
                        ext = Path(cite["source"]).suffix.lower()
                        if ext in (".png", ".jpg", ".jpeg"):
                            st.image(cite["source"])


def main() -> None:
    """Main application entry point."""
    app_config = AppConfig()
    st.set_page_config(page_title=app_config.title, layout="wide")
    st.title(app_config.title)
    st.markdown("Answer questions about PDFs, images, and videos using Amazon Bedrock Knowledge Bases.")

    config = init_config()
    render_upload_section(config)
    st.divider()
    render_query_section(config)


if __name__ == "__main__":
    main()
