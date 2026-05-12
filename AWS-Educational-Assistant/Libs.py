"""
AWS Educational Assistant - Core Library (2026 Edition)

Uses Amazon Bedrock Converse API with:
- Built-in Guardrails via guardrailConfig
- Proper system prompt separation
- Type-safe configuration with dataclasses
- Input sanitization
- Streaming via ConverseStream

References:
- Bedrock Converse API: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
- Guardrails + Converse: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html
- OWASP LLM Top 10 (2026): https://owasp.org/www-project-top-10-for-large-language-model-applications/
"""

import os
import sys
import json
import logging
from dataclasses import dataclass, field
from typing import Generator

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_community.chat_models import BedrockChat

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input, validate_input_length

load_dotenv()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BedrockConfig:
    """Immutable configuration for Bedrock API calls."""
    model_id: str = field(default_factory=lambda: os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6"))
    region: str = field(default_factory=lambda: os.environ.get("AWS_REGION", "us-east-1"))
    max_tokens: int = 4096
    temperature: float = 0.0
    top_p: float = 0.9
    guardrail_id: str = field(default_factory=lambda: os.environ.get("BEDROCK_GUARDRAIL_ID", ""))
    guardrail_version: str = field(default_factory=lambda: os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT"))


_config = BedrockConfig()
_client = boto3.client(
    "bedrock-runtime",
    region_name=_config.region,
    config=Config(read_timeout=120),
)


# ---------------------------------------------------------------------------
# Core: Converse API with Guardrails (2026 standard)
# ---------------------------------------------------------------------------

def converse_stream(
    prompt: str,
    system_prompt: str | None = None,
    config: BedrockConfig = _config,
) -> Generator[str, None, None]:
    """Stream a response using Bedrock Converse API with built-in Guardrails.

    This is the recommended approach for 2026:
    - Uses Converse API (model-agnostic, portable across providers)
    - Guardrails evaluated inline via guardrailConfig (no separate API call)
    - guardContent marks user input for targeted guardrail evaluation
    - System prompt is properly separated from user messages

    Args:
        prompt: User input text
        system_prompt: Optional system instructions (separated from user message)
        config: Bedrock configuration

    Yields:
        Text chunks from the model response
    """
    # Sanitize input
    prompt = sanitize_input(prompt)

    # Build messages with guardContent for targeted guardrail evaluation
    messages = [
        {
            "role": "user",
            "content": [
                {"guardContent": {"text": {"text": prompt}}}
            ],
        }
    ]

    # Build system prompt (guarded separately)
    system = []
    if system_prompt:
        system = [{"text": system_prompt}]

    # Build inference config
    inference_config = {
        "maxTokens": config.max_tokens,
        "temperature": config.temperature,
        "topP": config.top_p,
    }

    # Build request kwargs
    kwargs = {
        "modelId": config.model_id,
        "messages": messages,
        "inferenceConfig": inference_config,
    }
    if system:
        kwargs["system"] = system

    # Attach guardrail if configured
    if config.guardrail_id:
        kwargs["guardrailConfig"] = {
            "guardrailIdentifier": config.guardrail_id,
            "guardrailVersion": config.guardrail_version,
            "trace": "enabled",
            "streamProcessingMode": "sync",
        }

    try:
        response = _client.converse_stream(**kwargs)
        stream = response.get("stream")
        if stream:
            for event in stream:
                if "contentBlockDelta" in event:
                    delta = event["contentBlockDelta"].get("delta", {})
                    text = delta.get("text")
                    if text:
                        yield text
                elif "messageStop" in event:
                    stop_reason = event["messageStop"].get("stopReason", "")
                    if stop_reason == "guardrail_intervened":
                        logger.warning("Guardrail intervened on output")
                elif "metadata" in event:
                    trace = event["metadata"].get("trace")
                    if trace:
                        logger.info("Guardrail trace: %s", json.dumps(trace, default=str))
    except _client.exceptions.ValidationException as e:
        logger.error("Bedrock validation error: %s", e)
        yield "An error occurred processing your request."
    except Exception as e:
        logger.error("Bedrock API error: %s", e)
        yield "An error occurred. Please try again."


# Legacy alias for backward compatibility
def call_claude_sonet_stream(prompt: str, system_prompt: str | None = None) -> Generator[str, None, None]:
    """Legacy wrapper — delegates to converse_stream."""
    return converse_stream(prompt, system_prompt=system_prompt)


# ---------------------------------------------------------------------------
# Educational Functions
# ---------------------------------------------------------------------------

def rewrite_document(input_topic: str, subject_area: str, audience_level: str) -> Generator[str, None, None]:
    """Generate educational content for a given topic."""
    system = (
        f"You are an expert educator with deep knowledge in {subject_area}. "
        f"Create content suitable for {audience_level}."
    )
    prompt = (
        f"Create an engaging and informative lesson on: '{input_topic}'\n\n"
        "Include: Introduction, Key Concepts, Practical Applications, "
        "Common Misconceptions, Summary, and Further Reading."
    )
    return converse_stream(prompt, system_prompt=system)


def summary_stream(
    input_text: str,
    summary_length: str = "medium",
    detail_level: str = "medium",
    use_case: str = "general",
) -> Generator[str, None, None]:
    """Summarize lecture/academic content with customizable parameters."""
    input_text = sanitize_input(input_text)

    length_map = {
        "short": "brief, capturing only essential details",
        "medium": "concise but comprehensive, covering key concepts",
        "long": "detailed and thorough",
    }
    detail_map = {
        "high": "deep analysis and critical points",
        "medium": "balanced level of detail",
    }
    use_case_map = {
        "study": "key points for understanding and retention",
        "exam preparation": "critical facts for quick revision",
        "research": "methodologies and key findings",
        "general": "well-rounded for a general audience",
    }

    system = "You are an academic summarization expert. Produce clear, accurate summaries."
    prompt = (
        f"Summarize the following content.\n"
        f"Length: {length_map.get(summary_length, length_map['medium'])}\n"
        f"Detail: {detail_map.get(detail_level, detail_map['medium'])}\n"
        f"Focus: {use_case_map.get(use_case, use_case_map['general'])}\n\n"
        f"<content>{input_text}</content>"
    )
    return converse_stream(prompt, system_prompt=system)


def query_document(question: str, docs: str) -> str:
    """Answer a question based on lecture content."""
    question = sanitize_input(question, max_length=1000)
    docs_text = sanitize_input(str(docs))

    system = (
        "You are an educational assistant. Answer based solely on the provided "
        "lecture content. If the answer is not in the content, say so."
    )
    prompt = (
        f"<lecture_content>{docs_text}</lecture_content>\n\n"
        f"Question: {question}"
    )
    return "".join(chunk for chunk in converse_stream(prompt, system_prompt=system) if chunk)


def create_questions(input_text: str) -> Generator[str, None, None]:
    """Generate multiple-choice questions from content."""
    input_text = sanitize_input(str(input_text))

    system = (
        "You are an expert at creating multiple-choice questions. "
        "Create questions that assess comprehension, critical thinking, and application. "
        "Format: numbered questions with A-D options and the correct answer marked."
    )
    prompt = (
        "Create 20 multiple-choice questions from this content:\n\n"
        f"<text>{input_text}</text>"
    )
    return converse_stream(prompt, system_prompt=system)


def suggest_writing_document(input_text: str) -> Generator[str, None, None]:
    """Suggest improvements for a syllabus/course document."""
    input_text = sanitize_input(str(input_text))

    system = (
        "You are an experienced instructional designer. Review content and suggest "
        "improvements for: course overview, learning outcomes, structure, assessment, "
        "materials, policies, schedule, and engagement."
    )
    prompt = f"Review and improve this syllabus:\n\n<text>{input_text}</text>"
    return converse_stream(prompt, system_prompt=system)


def search(question: str, callback) -> dict:
    """RAG search using Amazon Knowledge Bases."""
    question = sanitize_input(question, max_length=1000)

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.environ.get("KNOWLEDGE_BASE_ID", "F3BT8DD8E8"),
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 3}},
    )

    llm = BedrockChat(
        model_id=_config.model_id,
        model_kwargs={"max_tokens": 2000},
        streaming=True,
        callbacks=[callback],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )
    return chain.invoke(question)
