import os
import sys
from dataclasses import dataclass

import streamlit as st
import boto3
import botocore.config

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input


@dataclass(frozen=True)
class TranslationConfig:
    region: str = os.environ.get("AWS_REGION", "us-east-1")
    guardrail_id: str = os.environ.get("BEDROCK_GUARDRAIL_ID", "")
    guardrail_version: str = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")
    max_tokens: int = 10000
    temperature: float = 0.0
    top_p: float = 0.5


CFG = TranslationConfig()

_boto_config = botocore.config.Config(connect_timeout=300, read_timeout=120)
session = boto3.Session()
bedrock = session.client("bedrock", region_name=CFG.region)
bedrock_runtime = session.client("bedrock-runtime", region_name=CFG.region, config=_boto_config)
translate = session.client("translate", region_name=CFG.region)


def _guardrail_config() -> dict:
    if CFG.guardrail_id:
        return {
            "guardrailIdentifier": CFG.guardrail_id,
            "guardrailVersion": CFG.guardrail_version,
        }
    return {}


def _converse(model_id: str, system_prompt: str, user_text: str) -> str:
    kwargs: dict = {
        "modelId": model_id,
        "system": [{"text": system_prompt}],
        "messages": [{"role": "user", "content": [{"text": user_text}]}],
        "inferenceConfig": {
            "maxTokens": CFG.max_tokens,
            "temperature": CFG.temperature,
            "topP": CFG.top_p,
        },
    }
    gc = _guardrail_config()
    if gc:
        kwargs["guardrailConfig"] = gc
    response = bedrock_runtime.converse(**kwargs)
    return response["output"]["message"]["content"][0]["text"]


def parse_xml(xml: str, tag: str) -> str:
    temp = xml.split(">")
    tag_to_extract = "</" + tag
    for line in temp:
        if tag_to_extract in line:
            return line.replace(tag_to_extract, "")
    return ""


@st.cache_data
def lst_langs() -> list:
    return translate.list_languages()["Languages"]


@st.cache_data
def lst_models() -> list:
    return bedrock.list_foundation_models(
        byProvider="Anthropic",
        byOutputModality="TEXT",
        byInferenceType="ON_DEMAND",
    )["modelSummaries"]


def transl_txt_bedrock(input_txt: str, src_lang: str, tgt_lang: str, model_id: str) -> str:
    system_prompt = (
        "You are a professional translator. Translate the given text from the source language "
        "to the target language accurately, preserving the original meaning. "
        "Only output the translated text."
    )
    user_text = sanitize_input(
        f"Source language: {src_lang}\nTarget language: {tgt_lang}\n\nText to translate:\n{input_txt}"
    )
    return _converse(model_id, system_prompt, user_text)


def transl_chat_bedrock(input_txt: str, tgt_lang: str, model_id: str) -> str:
    system_prompt = (
        "You are a multilingual assistant. Respond to the user's message in the specified target language. "
        "Only output the response in the target language."
    )
    user_text = sanitize_input(
        f"Target language: {tgt_lang}\n\nText to respond to:\n{input_txt}"
    )
    result = _converse(model_id, system_prompt, user_text)
    print("bedrock" + result)
    return result


def analyze_responses(input_txt: str, bedrock_txt: str, model_id: str) -> str:
    system_prompt = (
        "You are a professional translator tasked with reviewing and analyzing translated text. "
        "Evaluate the translation for accuracy, fluency, and adherence to the original context. "
        "Provide your analysis in English."
    )
    user_text = sanitize_input(
        f"Original text: {input_txt}\n\nTranslated text: {bedrock_txt}"
    )
    return _converse(model_id, system_prompt, user_text)
