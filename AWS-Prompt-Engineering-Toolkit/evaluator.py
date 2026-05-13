"""Evaluate prompts across multiple Bedrock models using the Converse API."""

import time
import boto3

bedrock = boto3.client("bedrock-runtime")


def invoke_model(model_id: str, prompt: str, max_tokens: int = 1024) -> dict:
    """Call Bedrock Converse API for a single model and measure latency/tokens."""
    start = time.perf_counter()
    response = bedrock.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    latency = time.perf_counter() - start

    usage = response.get("usage", {})
    output_text = response["output"]["message"]["content"][0]["text"]

    return {
        "model_id": model_id,
        "output": output_text,
        "latency_s": round(latency, 3),
        "input_tokens": usage.get("inputTokens", 0),
        "output_tokens": usage.get("outputTokens", 0),
    }


def compare_models(model_ids: list[str], prompt: str, max_tokens: int = 1024) -> list[dict]:
    """Run the same prompt against multiple models and return comparison results."""
    results = []
    for model_id in model_ids:
        try:
            result = invoke_model(model_id, prompt, max_tokens)
        except Exception as e:
            result = {
                "model_id": model_id,
                "output": f"ERROR: {e}",
                "latency_s": 0,
                "input_tokens": 0,
                "output_tokens": 0,
            }
        results.append(result)
    return results
