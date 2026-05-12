"""Location Analysis System - Bedrock Converse API integration."""

import os
import sys
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Generator, Optional

import boto3
from botocore.config import Config
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BedrockConfig:
    model_id: str = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6")
    region: str = os.environ.get("AWS_REGION", "us-east-1")


_config = BedrockConfig()
_client = boto3.client(
    "bedrock-runtime",
    region_name=_config.region,
    config=Config(read_timeout=120),
)

SYSTEM_PROMPT = "You are a helpful location analysis assistant. Provide detailed, accurate analysis."


def _guardrail_config() -> Optional[dict]:
    gid = os.environ.get("BEDROCK_GUARDRAIL_ID")
    if gid:
        return {"guardrailIdentifier": gid, "guardrailVersion": "DRAFT"}
    return None


def _stream_converse(messages: list, max_tokens: int = 4096, temperature: float = 0.0) -> Generator[str, None, None]:
    """Core streaming helper using converse_stream."""
    kwargs: dict = {
        "modelId": _config.model_id,
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": messages,
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
    }
    gc = _guardrail_config()
    if gc:
        kwargs["guardrailConfig"] = gc
    try:
        response = _client.converse_stream(**kwargs)
        for event in response.get("stream", []):
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"].get("delta", {})
                text = delta.get("text")
                if text:
                    yield text
    except Exception as e:
        logger.error(f"Converse stream error: {e}")
        raise


def call_claude_sonet_stream(prompt: str) -> Generator[str, None, None]:
    prompt = sanitize_input(prompt)
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    yield from _stream_converse(messages, max_tokens=4000, temperature=1.0)


def get_bytesio_from_bytes(image_bytes: bytes) -> BytesIO:
    return BytesIO(image_bytes)


def get_base64_from_bytes(image_bytes: bytes) -> str:
    import base64
    return base64.b64encode(image_bytes).decode("utf-8")


def get_bytes_from_file(file_path: str) -> bytes:
    resolved = os.path.realpath(file_path)
    with open(resolved, "rb") as f:
        return f.read()


def get_response_from_model(prompt_content: str, image_bytes: Optional[bytes] = None) -> Generator[str, None, None]:
    prompt_content = sanitize_input(prompt_content)
    content: list = []
    if image_bytes:
        content.append({
            "image": {
                "format": "jpeg",
                "source": {"bytes": image_bytes},
            }
        })
    content.append({"text": prompt_content})
    messages = [{"role": "user", "content": content}]
    yield from _stream_converse(messages, max_tokens=10000)


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
