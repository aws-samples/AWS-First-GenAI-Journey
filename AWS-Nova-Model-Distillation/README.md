# Amazon Nova Model Distillation

Demo of Amazon Nova Model Distillation — creating smaller, faster models from larger ones using Amazon Bedrock.

## Overview

Model distillation transfers knowledge from a large "teacher" model to a smaller "student" model, producing a compact model that retains much of the teacher's capability at lower latency and cost.

This demo uses Amazon Bedrock's `create_model_customization_job` API with `customizationType=DISTILLATION`.

## Architecture

- **Teacher models**: Nova Pro, Nova Lite, Nova Premier
- **Student models**: Nova Micro, Nova Lite
- **Training data**: JSONL file in S3 with prompt/completion pairs
- **Output**: Distilled custom model deployed via Bedrock

## Prerequisites

- AWS account with Bedrock access enabled for Nova models
- IAM role with Bedrock and S3 permissions
- Training data in S3 (JSONL format)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

1. Select teacher and student models
2. Configure distillation parameters (epochs, batch size, learning rate)
3. Launch the distillation job
4. Monitor job status until completion

## Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit UI for configuring and launching distillation |
| `distill.py` | Bedrock API calls for distillation job management |
