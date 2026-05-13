# AWS GenAI Data Analyst

Chat with your data: upload a CSV, ask questions in natural language, and get charts and insights powered by Amazon Bedrock.

## Features

- Upload any CSV file and preview the data
- Ask questions in natural language
- AI generates pandas code via Amazon Bedrock Converse API (Claude 3 Sonnet)
- Automatic chart generation with matplotlib
- Conversational chat interface

## Prerequisites

- Python 3.9+
- AWS credentials configured with Bedrock access
- Claude 3 Sonnet model enabled in us-east-1

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## How It Works

1. Upload a CSV file
2. The app reads column names and types
3. Ask a question in the chat input
4. Bedrock generates pandas code to answer your question
5. Code executes safely and results/charts are displayed

## Architecture

- **Frontend**: Streamlit
- **AI**: Amazon Bedrock Converse API (Claude 3 Sonnet)
- **Data Processing**: pandas + matplotlib
