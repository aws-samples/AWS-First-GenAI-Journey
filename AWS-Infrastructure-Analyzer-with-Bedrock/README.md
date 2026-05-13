# AWS Infrastructure Analyzer with Bedrock

Analyze AWS CloudFormation and Terraform templates for security issues, cost optimization, and best practices using Amazon Bedrock's Converse API.

## Features

- Upload YAML, JSON, or HCL infrastructure templates
- AI-powered analysis using Claude on Amazon Bedrock
- Security vulnerability detection
- Cost optimization recommendations
- Best practice compliance checks
- Findings categorized by severity (CRITICAL/HIGH/MEDIUM/LOW/INFO)

## Prerequisites

- Python 3.9+
- AWS credentials configured with Bedrock access
- Amazon Bedrock model access enabled for Claude 3 Sonnet

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Open the browser, upload a CloudFormation/Terraform template, and click "Analyze Template" to get findings.

## Architecture

- **app.py** - Streamlit web interface for file upload and results display
- **analyzer.py** - Bedrock Converse API integration with structured output parsing
