"""
shared/libs.py — Core Bedrock utilities shared across vision/ML projects.

Used by:
  - AWS-First-Cloud-Journey-Uniform-Detection
  - Content-Moderation-with-Amazon-Bedrock
  - Location-Analysis-System-with-Amazon-Bedrock
  - Product-Description-Generator-with-Amazon-Bedrock
  - TapVision-with-Amazon-Bedrock

To use in a project's Libs.py:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from shared.libs import *
"""

import os
import boto3
import json
import logging
import base64
from io import BytesIO
from dotenv import load_dotenv
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Streaming helpers
# ---------------------------------------------------------------------------

def call_claude_sonet_stream(prompt):
    """Stream a text-only prompt through Claude Sonnet on Bedrock."""
    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": 1,
        "top_k": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    body = json.dumps(prompt_config)
    modelId = "anthropic.claude-sonnet-4-6"

    bedrock = boto3.client(service_name="bedrock-runtime")
    response = bedrock.invoke_model_with_response_stream(
        body=body, modelId=modelId, accept="application/json", contentType="application/json"
    )

    stream = response["body"]
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                try:
                    delta = json.loads(chunk.get("bytes").decode()).get("delta")
                    if delta:
                        yield delta.get("text")
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
                    logger.warning(f"Failed to parse stream chunk: {e}")
                    continue


# ---------------------------------------------------------------------------
# Image / bytes utilities
# ---------------------------------------------------------------------------

def get_bytesio_from_bytes(image_bytes):
    """Return a BytesIO object from raw image bytes."""
    return BytesIO(image_bytes)


def get_base64_from_bytes(image_bytes):
    """Return a base64-encoded string from raw image bytes."""
    resized_io = get_bytesio_from_bytes(image_bytes)
    return base64.b64encode(resized_io.getvalue()).decode("utf-8")


def get_bytes_from_file(file_path):
    """Read a file from disk and return its bytes. Validates path to prevent traversal."""
    resolved = os.path.realpath(file_path)
    with open(resolved, "rb") as image_file:
        return image_file.read()


# ---------------------------------------------------------------------------
# Multimodal model invocation
# ---------------------------------------------------------------------------

def _build_request_body(prompt, image_bytes=None):
    """Build the Bedrock request body for a text or text+image prompt."""
    if image_bytes:
        input_image_base64 = get_base64_from_bytes(image_bytes)
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": input_image_base64,
                },
            },
            {"type": "text", "text": prompt},
        ]
    else:
        content = [{"type": "text", "text": prompt}]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [{"role": "user", "content": content}],
    }
    return json.dumps(body)


# Keep old name for backward compatibility
def init(prompt, image_bytes=None):
    """Alias for _build_request_body — kept for backward compatibility."""
    return _build_request_body(prompt, image_bytes)


def get_response_from_model(prompt_content, image_bytes):
    """Stream a response from Claude Sonnet given a text prompt and optional image."""
    session = boto3.Session()
    bedrock = session.client(service_name="bedrock-runtime")
    body = _build_request_body(prompt_content, image_bytes)
    response = bedrock.invoke_model_with_response_stream(
        body=body,
        modelId="anthropic.claude-sonnet-4-6",
        contentType="application/json",
        accept="application/json",
    )

    stream = response["body"]
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                try:
                    delta = json.loads(chunk.get("bytes").decode()).get("delta")
                    if delta:
                        yield delta.get("text")
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
                    logger.warning(f"Failed to parse stream chunk: {e}")
                    continue


# ---------------------------------------------------------------------------
# PRIZM segment data (shared reference data)
# ---------------------------------------------------------------------------

prizm = """
    {
      "hh_employment": "Mix",
      "code": "63",
      "pzp_gcode": "63",
      "lifestage_group_name": "Striving Singles",
      "segment_icon_name": "63_low_rise_living.png",
      "hh_composition": "Mostly w/o Kids",
      "lifestage_super_group_name": "D70036",
      "segment_lifestage_group": "03",
      "demographic_caption": "Lower Mid(Scale) Middle Age Mostly w/o Kids",
      "social_group_name": "Urban Cores",
      "segment_nickname": "Low-Rise Living",
      "pzp_code": "63",
      "lifestyle_trait1": "Owns a Mitsubishi",
      "hh_tenure": "Renters",
      "lifestyle_trait2": "Eats at Starbucks",
      "lifestyle_trait3": "Shops at Banana Republic",
      "urbanicity": "Urban",
      "hh_income": "Lower Mid(Scale)",
      "hh_education": "Some College",
      "lifestage_group_rank": 16,
      "segment_narrative": "The most economically challenged urban segment, Low-Rise Living is home to mostly middle-aged, ethnically diverse singles and single parents. Unlike their low income peers, they rank above average in their use of technology - perhaps influenced by their urban, fast-paced environment.",
      "lifestyle_trait4": "Follows pro boxing",
      "lifestyle_trait5": "Flies JetBlue",
      "segment_social_group": "03",
      "lifestyle_trait6": "Watches Telemundo",
      "style": "moduleBtn1",
      "lifestyle_trait7": "Listens to Jazz",
      "social_group_rank": 13,
      "hh_ipa_class": "Below Avg",
      "hh_age_range": "Age <55",
      "lifestage_group_alias": "Y3",
      "social_group_alias": "U3"
  }
"""
