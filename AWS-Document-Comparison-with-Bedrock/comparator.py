import boto3
from pypdf import PdfReader


def extract_text(pdf_file):
    """Extract text from an uploaded PDF file."""
    reader = PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def compare_documents(text1, text2, model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
    """Compare two documents using Bedrock Converse API and return structured differences."""
    client = boto3.client("bedrock-runtime")
    prompt = (
        "Compare the following two documents. Identify and list the key differences "
        "in a structured format with sections: 'Added', 'Removed', and 'Modified'. "
        "For each difference, quote the relevant text.\n\n"
        f"--- DOCUMENT 1 ---\n{text1}\n\n--- DOCUMENT 2 ---\n{text2}"
    )
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    return response["output"]["message"]["content"][0]["text"]
