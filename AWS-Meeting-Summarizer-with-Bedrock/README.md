# Meeting Summarizer with Amazon Bedrock

Transcribe meeting recordings and extract key points, action items, decisions, and attendee contributions using Amazon Transcribe and Amazon Bedrock.

## Architecture

1. Upload audio/video via Streamlit UI
2. File stored in S3, transcribed with Amazon Transcribe (speaker diarization enabled)
3. Transcript summarized using Bedrock Converse API (Claude 3 Sonnet)
4. Results displayed: summary, action items, decisions, attendee contributions

## Prerequisites

- AWS account with access to Amazon Transcribe and Bedrock (Claude 3 Sonnet enabled)
- S3 bucket for storing uploaded audio files
- AWS credentials configured (`aws configure` or IAM role)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Enter your S3 bucket name
2. Upload a meeting recording (mp3, mp4, wav, m4a, webm)
3. Click "Transcribe & Summarize"
4. View the transcript and AI-generated meeting analysis

## AWS Services Used

- **Amazon S3** - Audio file storage
- **Amazon Transcribe** - Speech-to-text with speaker identification
- **Amazon Bedrock** - Meeting summarization via Converse API
