"""Core RAG logic using Amazon Bedrock Knowledge Bases."""

import os
import boto3
from dataclasses import dataclass


@dataclass
class RAGConfig:
    region: str = os.environ.get("AWS_REGION", "us-east-1")
    kb_id: str = os.environ.get("BEDROCK_KB_ID", "")
    s3_bucket: str = os.environ.get("S3_BUCKET", "")
    model_id: str = os.environ.get("MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")


def index_document(file_bytes: bytes, file_name: str, config: RAGConfig) -> str:
    """Upload a document to S3 for Knowledge Base ingestion."""
    s3 = boto3.client("s3", region_name=config.region)
    key = f"uploads/{file_name}"
    s3.put_object(Bucket=config.s3_bucket, Key=key, Body=file_bytes)
    return f"s3://{config.s3_bucket}/{key}"


def query(question: str, config: RAGConfig) -> dict:
    """Retrieve from KB and generate answer via retrieve_and_generate."""
    client = boto3.client("bedrock-agent-runtime", region_name=config.region)
    response = client.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": config.kb_id,
                "modelArn": f"arn:aws:bedrock:{config.region}::foundation-model/{config.model_id}",
            },
        },
    )
    output_text = response["output"]["text"]
    citations = []
    for citation in response.get("citations", []):
        for ref in citation.get("retrievedReferences", []):
            loc = ref.get("location", {})
            citations.append({
                "text": ref.get("content", {}).get("text", ""),
                "source": loc.get("s3Location", {}).get("uri", ""),
            })
    return {"answer": output_text, "citations": citations}
