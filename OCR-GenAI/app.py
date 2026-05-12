#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import base64
import io
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import boto3
import streamlit as st
from botocore.config import Config
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

SYSTEM_PROMPT = (
    "You are a document OCR assistant. Extract all text from images accurately, "
    "preserving the original structure. Separate each line with a newline character."
)


@dataclass(frozen=True)
class BedrockConfig:
    model_id: str = os.environ.get("MODEL_ID", "anthropic.claude-sonnet-4-6")
    region: str = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
    guardrail_id: Optional[str] = os.environ.get("BEDROCK_GUARDRAIL_ID")


def get_bedrock_client(cfg: BedrockConfig):
    return boto3.client(
        "bedrock-runtime",
        region_name=cfg.region,
        config=Config(read_timeout=120),
    )


def run_ocr(client, cfg: BedrockConfig, base64_image: str) -> str:
    user_text = sanitize_input(
        "Extract all text from the image and separate each line or text segment with a newline character."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"image": {"format": "jpeg", "source": {"bytes": base64.b64decode(base64_image)}}},
                {"text": user_text},
            ],
        }
    ]

    kwargs: dict = {
        "modelId": cfg.model_id,
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": messages,
        "inferenceConfig": {"maxTokens": 2000, "temperature": 0, "topP": 0.999},
    }
    if cfg.guardrail_id:
        kwargs["guardrailConfig"] = {"guardrailIdentifier": cfg.guardrail_id, "guardrailVersion": "DRAFT"}

    response = client.converse(**kwargs)
    text = response["output"]["message"]["content"][0]["text"]
    return "  \n".join(text.split("\n"))


def set_page_config():
    st.set_page_config(layout="wide", page_title="Document Understanding System", page_icon="📄")


def add_custom_css():
    st.markdown("""
        <style>
        .main { padding: 2rem; }
        .stButton>button { width: 100%; }
        .upload-text { text-align: center; padding: 2rem; border: 2px dashed #cccccc; border-radius: 5px; }
        </style>
    """, unsafe_allow_html=True)


def validate_image(uploaded_file) -> tuple[bool, str]:
    if uploaded_file is None:
        return False, "No file uploaded"
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Please upload {', '.join(ALLOWED_EXTENSIONS)}"
    if uploaded_file.size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE/1024/1024}MB"
    return True, ""


def process_image(image: Image.Image, max_size: tuple[int, int] = (800, 800)) -> Image.Image:
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size)
    return image


def display_image_info(image: Image.Image):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Width", f"{image.size[0]}px")
    with col2:
        st.metric("Height", f"{image.size[1]}px")
    with col3:
        st.metric("Format", image.format)


def main():
    cfg = BedrockConfig()
    try:
        client = get_bedrock_client(cfg)
    except Exception as e:
        st.error(f"Error initializing the application: {str(e)}")
        return

    set_page_config()
    add_custom_css()

    st.title("📄 Document Understanding System")
    st.markdown("Upload your document to extract and analyze text using OCR technology.")

    with st.sidebar:
        st.header("⚙️ Configuration")
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
        show_debug_info = st.checkbox("Show Debug Information", value=False)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose an image", type=ALLOWED_EXTENSIONS,
            help=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

        if uploaded_file is not None:
            is_valid, error_message = validate_image(uploaded_file)
            if not is_valid:
                st.error(error_message)
                return

            try:
                image = Image.open(uploaded_file)
                image = process_image(image)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
                if show_debug_info:
                    display_image_info(image)

                buffered = io.BytesIO()
                image.save(buffered, format=image.format or "JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                return

    with col2:
        st.subheader("📑 Extracted Results")
        if uploaded_file is not None:
            with st.spinner("Processing document..."):
                try:
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)

                    text = run_ocr(client, cfg, base64_image)
                    st.success("Document processed successfully!")

                    tab1, tab2 = st.tabs(["Extracted Text", "Analysis"])
                    with tab1:
                        st.markdown("### 📝 Extracted Text")
                        st.markdown(text)
                        if st.button("📋 Copy to Clipboard"):
                            st.session_state["clipboard"] = text

                    with tab2:
                        st.markdown("### 📊 Document Analysis")
                        word_count = len(text.split())
                        char_count = len(text)
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Word Count", word_count)
                        with c2:
                            st.metric("Character Count", char_count)

                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                    if show_debug_info:
                        st.exception(e)


if __name__ == "__main__":
    main()
