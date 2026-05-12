# Multimodal RAG with Amazon Bedrock

Answer questions about PDFs, images, and videos using Amazon Bedrock Knowledge Bases.

## Architecture

```
┌──────────────┐     ┌─────────────┐     ┌──────────────────────┐
│  Streamlit   │────▶│   Amazon S3  │────▶│  Bedrock Knowledge   │
│   (app.py)   │     │  (uploads)   │     │       Base           │
└──────┬───────┘     └─────────────┘     └──────────┬───────────┘
       │                                             │
       │         ┌───────────────────────┐           │
       └────────▶│  Bedrock Converse API │◀──────────┘
                 │  (retrieve & generate)│
                 └───────────────────────┘
```

## Prerequisites

- AWS account with Bedrock access enabled
- Amazon Bedrock Knowledge Base configured with S3 data source
- Python 3.11+

## Setup

```bash
pip install -r requirements.txt

export AWS_REGION=us-east-1
export BEDROCK_KB_ID=your-knowledge-base-id
export S3_BUCKET=your-s3-bucket-name
export MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0  # optional
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Configure your KB ID and S3 bucket in the sidebar
2. Upload PDFs, images, or videos
3. Ask questions — the system retrieves relevant context and generates answers

## Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit UI for upload and Q&A |
| `rag_engine.py` | Core RAG logic (S3 upload + retrieve_and_generate) |
| `requirements.txt` | Python dependencies |
