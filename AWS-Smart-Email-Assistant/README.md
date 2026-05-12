# AWS Smart Email Assistant

AI-powered email assistant that helps you draft replies, summarize threads, extract action items, and translate emails using Amazon Bedrock.

## Features

- **Draft Reply** – Generate professional email replies matching the original tone
- **Summarize Thread** – Get structured summaries of long email conversations
- **Extract Action Items** – Pull out tasks, owners, and deadlines from threads
- **Translate** – Translate email threads to any target language

## Architecture

- **Frontend**: Streamlit
- **AI Backend**: Amazon Bedrock Converse API (Claude 3 Sonnet)
- **Region**: us-east-1

## Prerequisites

- AWS credentials configured with Bedrock access
- Python 3.9+

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Paste an email thread into the text area
2. Select an action (Reply / Summarize / Extract Actions / Translate)
3. Click **Process** and view the result
4. Use the copy button on the code block to copy the output
