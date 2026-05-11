# AWS OCR with Amazon Bedrock

A powerful OCR (Optical Character Recognition) system powered by Claude 3, implemented with both direct Boto3 and LangChain approaches.

> **Note**: This project was previously also available as `OCR-GenAI` — both were identical. Consolidated here.

## Project Structure

```
.
├── app.py                    # Main application entry point
├── claude3_boto3_ocr.py      # Boto3 implementation
├── claude3_langchain_ocr.py  # LangChain implementation
└── requirements.txt
```

## Features

- Dual implementation (Boto3 and LangChain)
- High-accuracy text extraction
- Multi-language support
- Table structure recognition
- Layout preservation
- Support for images (JPG, PNG, TIFF, BMP) and documents (PDF)

## Prerequisites

- Python 3.12+
- AWS Account with Bedrock access and appropriate IAM permissions
- Claude 3 model access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aws-samples/AWS-First-GenAI-Journey.git
cd AWS-First-GenAI-Journey/AWS-OCR-with-Amazon-Bedrock
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## Usage

### Using Boto3 Implementation

```python
from claude3_boto3_ocr import extract_text

text = extract_text('path/to/your/image.jpg')
```

### Using LangChain Implementation

```python
from claude3_langchain_ocr import process_document

result = process_document('path/to/your/document.pdf')
```

### Running the Application

```bash
python app.py --input path/to/image --output path/to/result
```

## Best Practices

- Ensure good image quality (minimum 300 DPI)
- Proper lighting and contrast
- Implement proper error handling for API calls
- Monitor API usage and costs

## Security

- Keep AWS credentials secure
- Use IAM roles with minimum required permissions
- Implement input validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
