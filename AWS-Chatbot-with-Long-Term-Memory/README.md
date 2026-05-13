# 🧠 Chatbot with Long-Term Memory

A Streamlit chatbot that remembers past conversations using Amazon Bedrock and DynamoDB.

## Architecture

- **Amazon Bedrock** (Claude 3 Haiku) - LLM for chat responses and summarization
- **Amazon DynamoDB** - Persistent conversation storage per user
- **Streamlit** - Web UI for the chat interface

## Prerequisites

- AWS account with Bedrock model access (Claude 3 Haiku)
- DynamoDB table `ChatbotMemory` with partition key `user_id` (String) and sort key `timestamp` (String)
- AWS credentials configured (`~/.aws/credentials` or IAM role)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Features

- User login with persistent conversation history
- Real-time chat with Amazon Bedrock Converse API
- Conversation context maintained across sessions
- Memory summary generation on demand

## DynamoDB Table Schema

| Attribute | Type | Key |
|-----------|------|-----|
| user_id | String | Partition Key |
| timestamp | String | Sort Key |
| role | String | - |
| content | String | - |
