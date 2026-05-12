"""
Security utilities for GenAI applications.
Provides input sanitization, validation, and Amazon Bedrock Guardrails integration.

References:
- OWASP Top 10 for LLM & Agentic Applications (2026)
- Amazon Bedrock Guardrails: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
"""

import os
import re
import json
import logging

logger = logging.getLogger(__name__)

MAX_INPUT_LENGTH = 50000  # 50K chars max for LLM input
MAX_PROMPT_LENGTH = 1000  # 1K chars for short user prompts/questions

# Patterns that may indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|context)",
    r"disregard\s+(all\s+)?(previous|above|prior)",
    r"you\s+are\s+now\s+a",
    r"new\s+instructions?:",
    r"system\s*prompt:",
    r"<\s*/?\s*system\s*>",
]


def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Sanitize user input before embedding in LLM prompts.
    
    - Truncates to max_length
    - Escapes XML-like tags that could interfere with prompt structure
    - Logs warning if injection patterns detected (does not block)
    """
    if not text:
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Escape XML tags that could break prompt delimiters
    text = re.sub(r'<(/?)(?:system|human|assistant|response|text|context)', r'&lt;\1', text, flags=re.IGNORECASE)
    
    return text


def validate_input_length(text: str, max_length: int = MAX_PROMPT_LENGTH) -> tuple[bool, str]:
    """Validate input length. Returns (is_valid, error_message)."""
    if not text or not text.strip():
        return False, "Input cannot be empty."
    if len(text) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters."
    return True, ""


def detect_injection(text: str) -> bool:
    """Detect potential prompt injection attempts. Returns True if suspicious."""
    if not text:
        return False
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in INJECTION_PATTERNS)


# ---------------------------------------------------------------------------
# Amazon Bedrock Guardrails Integration (2026)
# ---------------------------------------------------------------------------

class BedrockGuardrail:
    """Wrapper for Amazon Bedrock Guardrails ApplyGuardrail API.
    
    For standalone guardrail evaluation (e.g., pre-check before non-Bedrock LLMs).
    
    NOTE (2026 Best Practice): If using Bedrock Converse API, prefer passing
    guardrailConfig directly in the converse/converse_stream call instead of
    using this standalone wrapper. See AWS-Educational-Assistant/Libs.py for example.
    
    Provides centralized content filtering for:
    - Prompt attack detection (prompt injection, jailbreak)
    - Sensitive information filtering (PII)
    - Topic denial
    - Content filtering (hate, violence, sexual, misconduct)
    - Multimodal content filtering (images, 88% block rate as of April 2026)
    
    Usage:
        guardrail = BedrockGuardrail(guardrail_id="your-id", guardrail_version="DRAFT")
        result = guardrail.apply(text="user input", source="INPUT")
        if result.is_blocked:
            st.error(result.message)
        else:
            # proceed with LLM call using result.output
    
    Environment variables:
        BEDROCK_GUARDRAIL_ID: The guardrail identifier
        BEDROCK_GUARDRAIL_VERSION: Version (default: "DRAFT")
        AWS_REGION: AWS region for the Bedrock client
    """

    def __init__(self, guardrail_id=None, guardrail_version=None, region=None):
        import boto3
        self.guardrail_id = guardrail_id or os.environ.get("BEDROCK_GUARDRAIL_ID")
        self.guardrail_version = guardrail_version or os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    def apply(self, text: str, source: str = "INPUT") -> "GuardrailResult":
        """Apply guardrail to text content.
        
        Args:
            text: The text to evaluate
            source: "INPUT" for user prompts, "OUTPUT" for model responses
            
        Returns:
            GuardrailResult with is_blocked, output, and action details
        """
        if not self.guardrail_id:
            logger.warning("No BEDROCK_GUARDRAIL_ID configured, skipping guardrail check")
            return GuardrailResult(is_blocked=False, output=text)

        try:
            response = self.client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source=source,
                content=[{"text": {"text": text}}],
            )
            action = response.get("action", "NONE")
            if action == "GUARDRAIL_INTERVENED":
                outputs = response.get("outputs", [])
                message = outputs[0]["text"] if outputs else "Content blocked by guardrail."
                logger.info(f"Guardrail blocked {source}: action={action}")
                return GuardrailResult(
                    is_blocked=True,
                    output=message,
                    action=action,
                    assessments=response.get("assessments", []),
                )
            return GuardrailResult(is_blocked=False, output=text, action=action)
        except Exception as e:
            logger.error(f"Guardrail API error: {e}")
            # Fail-open: allow content through if guardrail service is unavailable
            return GuardrailResult(is_blocked=False, output=text, error=str(e))


class GuardrailResult:
    """Result from a Bedrock Guardrail evaluation."""

    def __init__(self, is_blocked: bool, output: str, action: str = "NONE",
                 assessments: list = None, error: str = None):
        self.is_blocked = is_blocked
        self.output = output
        self.action = action
        self.assessments = assessments or []
        self.error = error
