import boto3
import json
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ChatbotMemory")
bedrock = boto3.client("bedrock-runtime")


def save_message(user_id, role, content):
    table.put_item(Item={
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "role": role,
        "content": content,
    })


def get_history(user_id, limit=50):
    resp = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id),
        ScanIndexForward=True,
        Limit=limit,
    )
    return [{"role": item["role"], "content": [{"text": item["content"]}]} for item in resp["Items"]]


def summarize_history(user_id):
    history = get_history(user_id)
    if not history:
        return "No conversation history yet."
    transcript = "\n".join(f"{m['role']}: {m['content'][0]['text']}" for m in history)
    resp = bedrock.converse(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[{"role": "user", "content": [{"text": f"Summarize this conversation in 2-3 sentences:\n{transcript}"}]}],
    )
    return resp["output"]["message"]["content"][0]["text"]
