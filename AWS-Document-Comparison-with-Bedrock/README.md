# Document Comparison with Amazon Bedrock

Compare two PDF documents (contracts, policies, etc.) and highlight key differences using Amazon Bedrock's Converse API.

## Features

- Upload two PDF documents side-by-side
- Extract text automatically using pypdf
- Compare documents using Claude on Amazon Bedrock
- View structured differences: Added, Removed, and Modified sections

## Prerequisites

- Python 3.9+
- AWS credentials configured with Bedrock access
- Claude model enabled in your AWS region

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

1. Upload two PDF files
2. Review extracted text in the expander
3. Click "Compare Documents" to analyze differences
4. View the structured comparison results

## Architecture

- **app.py** - Streamlit UI with file upload and side-by-side display
- **comparator.py** - PDF text extraction and Bedrock Converse API integration
