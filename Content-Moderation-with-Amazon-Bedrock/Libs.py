import os, sys, logging
from dataclasses import dataclass
from typing import Generator, Optional
from io import BytesIO

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
    guardrail_id: Optional[str] = os.environ.get("BEDROCK_GUARDRAIL_ID")


_cfg = BedrockConfig()
_client = boto3.client(
    "bedrock-runtime",
    region_name=_cfg.region,
    config=Config(read_timeout=120),
)


def _guardrail_kwargs() -> dict:
    if _cfg.guardrail_id:
        return {"guardrailConfig": {"guardrailIdentifier": _cfg.guardrail_id, "guardrailVersion": "DRAFT"}}
    return {}


def _stream_converse(messages: list, system: Optional[list] = None) -> Generator[Optional[str], None, None]:
    kwargs: dict = {
        "modelId": _cfg.model_id,
        "messages": messages,
        "inferenceConfig": {"maxTokens": 4096, "temperature": 0},
        **_guardrail_kwargs(),
    }
    if system:
        kwargs["system"] = system
    response = _client.converse_stream(**kwargs)
    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            yield delta.get("text")


def call_claude_sonet_stream(prompt: str) -> Generator[Optional[str], None, None]:
    prompt = sanitize_input(prompt)
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    system = [{"text": "You are a helpful content moderation assistant."}]
    yield from _stream_converse(messages, system)


def get_bytesio_from_bytes(image_bytes: bytes) -> BytesIO:
    return BytesIO(image_bytes)


def get_base64_from_bytes(image_bytes: bytes) -> str:
    import base64
    return base64.b64encode(image_bytes).decode("utf-8")


def get_bytes_from_file(file_path: str) -> bytes:
    resolved = os.path.realpath(file_path)
    with open(resolved, "rb") as f:
        return f.read()


def init(prompt: str, image_bytes: Optional[bytes] = None) -> list:
    prompt = sanitize_input(prompt)
    content: list = []
    if image_bytes:
        content.append({"image": {"format": "jpeg", "source": {"bytes": image_bytes}}})
    content.append({"text": prompt})
    return [{"role": "user", "content": content}]


def get_response_from_model(prompt_content: str, image_bytes: Optional[bytes] = None) -> Generator[Optional[str], None, None]:
    messages = init(prompt_content, image_bytes)
    system = [{"text": "You are a helpful content moderation assistant."}]
    yield from _stream_converse(messages, system)


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
