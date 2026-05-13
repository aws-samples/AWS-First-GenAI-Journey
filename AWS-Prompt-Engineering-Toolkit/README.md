# AWS Prompt Engineering Toolkit

A Streamlit-based toolkit for testing and comparing prompts across multiple Amazon Bedrock models.

## Features

- **Prompt Templates**: Define prompts with `{{variable}}` placeholders
- **Multi-Model Comparison**: Run the same prompt against multiple Bedrock models simultaneously
- **Metrics Dashboard**: Compare latency, token usage, and response quality side by side
- **A/B Testing**: Quickly iterate on prompt variations and see how different models respond

## Prerequisites

- Python 3.10+
- AWS credentials configured with Bedrock access
- Model access enabled in your AWS account for the models you want to test

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

1. Select models from the sidebar
2. Enter a prompt template with `{{variables}}`
3. Fill in variable values
4. Click **Run Comparison** to see results

## Supported Models

- Anthropic Claude 3.5 Sonnet / Haiku
- Amazon Nova Pro / Lite / Micro
- Meta Llama 3 70B Instruct

## Architecture

- `app.py` — Streamlit UI for prompt input, model selection, and results display
- `evaluator.py` — Bedrock Converse API integration with latency and token tracking
