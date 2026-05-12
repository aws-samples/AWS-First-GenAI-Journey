"""Helper script to create Amazon Bedrock Guardrails via API."""
import boto3
import os


def create_guardrail():
    """Create a guardrail with content filters, topic denial, and PII detection."""
    region = os.environ.get("AWS_REGION", "us-east-1")
    name = os.environ.get("GUARDRAIL_NAME", "demo-guardrail")

    client = boto3.client("bedrock", region_name=region)

    response = client.create_guardrail(
        name=name,
        description="Demo guardrail with content filtering, PII detection, and topic denial",
        blockedInputMessaging="Your input was blocked by our content policy.",
        blockedOutputsMessaging="The model response was blocked by our content policy.",
        contentPolicyConfig={
            "filtersConfig": [
                {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH"},
            ]
        },
        topicPolicyConfig={
            "topicsConfig": [
                {
                    "name": "Financial Advice",
                    "definition": "Providing specific investment or financial planning advice",
                    "examples": [
                        "Which stocks should I buy?",
                        "How should I invest my money?",
                    ],
                    "type": "DENY",
                }
            ]
        },
        sensitiveInformationPolicyConfig={
            "piiEntitiesConfig": [
                {"type": "EMAIL", "action": "BLOCK"},
                {"type": "US_SOCIAL_SECURITY_NUMBER", "action": "BLOCK"},
                {"type": "PHONE", "action": "BLOCK"},
                {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
            ]
        },
    )

    guardrail_id = response["guardrailId"]
    print(f"Created guardrail: {guardrail_id} (version: {response['version']})")
    return guardrail_id


if __name__ == "__main__":
    create_guardrail()
