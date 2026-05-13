# Amazon Bedrock Guardrails Demo

Interactive demo showcasing Amazon Bedrock Guardrails features for responsible AI.

## Features

- **Content Filtering** – Block harmful content across categories (violence, hate, sexual, misconduct, prompt attacks)
- **PII Detection** – Detect and block personally identifiable information (SSN, email, phone, credit cards)
- **Topic Denial** – Deny responses on restricted topics (e.g., financial advice)
- **Prompt Attack Prevention** – Detect and block prompt injection and jailbreak attempts

## Prerequisites

- AWS account with Bedrock access enabled
- Python 3.9+
- AWS credentials configured (`aws configure` or IAM role)
- Model access enabled in Bedrock console

## Setup

```bash
pip install -r requirements.txt
```

### Create a Guardrail

```bash
export AWS_REGION=us-east-1
export GUARDRAIL_NAME=demo-guardrail
python guardrail_setup.py
```

This creates a guardrail with content filters, PII detection, and topic denial policies.

### Run the App

```bash
export GUARDRAIL_ID=<your-guardrail-id>
streamlit run app.py
```

## Usage

1. Enter your Guardrail ID in the sidebar
2. Select a test scenario (Content Filtering, PII Detection, Topic Denial, Prompt Attack)
3. Modify the input text or use the provided example
4. Click "Test Guardrail" to see the assessment results
5. Review the trace information to understand what was blocked and why

## Architecture

The app uses the Bedrock **Converse API** with `guardrailConfig` to apply guardrails inline during inference. Trace output shows detailed assessment results for each policy type.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `GUARDRAIL_ID` | Guardrail identifier | — |
| `GUARDRAIL_NAME` | Name for new guardrail | `demo-guardrail` |
