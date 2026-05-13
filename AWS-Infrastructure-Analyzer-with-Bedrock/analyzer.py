import boto3
import json

SYSTEM_PROMPT = """You are an AWS infrastructure security and cost optimization expert.
Analyze the provided CloudFormation/Terraform template and return a JSON array of findings.
Each finding must have: "severity" (CRITICAL/HIGH/MEDIUM/LOW/INFO), "category" (Security/Cost/BestPractice), "resource" (resource name), "issue" (description), "recommendation" (fix).
Return ONLY valid JSON array, no markdown or extra text."""


def analyze_template(template_content: str, filename: str) -> list:
    """Analyze an infrastructure template using Amazon Bedrock Converse API."""
    client = boto3.client("bedrock-runtime")
    response = client.converse(
        modelId="anthropic.claude-sonnet-4-6",
        system=[{"text": SYSTEM_PROMPT}],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Analyze this infrastructure template ({filename}) for security issues, cost optimization, and best practices:\n\n{template_content}"
                    }
                ],
            }
        ],
        inferenceConfig={"maxTokens": 4096, "temperature": 0.1},
    )
    result_text = response["output"]["message"]["content"][0]["text"]
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        start = result_text.find("[")
        end = result_text.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
        return [{"severity": "INFO", "category": "BestPractice", "resource": "N/A",
                 "issue": "Could not parse structured output", "recommendation": result_text}]
