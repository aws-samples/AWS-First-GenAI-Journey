# Amazon Bedrock Model Evaluator

A comprehensive tool for evaluating and benchmarking Amazon Bedrock models, including performance metrics, cost analysis, and reporting capabilities.

> **Note**: This project was previously also available as `GenAI-Model-Evaluator` — both were identical. Consolidated here.

## Project Structure

```
.
├── AnthropicTokenCounter.py          # Token counting utility
├── app.py                            # Main Streamlit application
├── evaluation_steps.py               # Evaluation procedures
├── knowledge_base_fetcher.py         # Knowledge base management
├── orchestration_helper.py           # Orchestration utilities
├── orchestration_rag_helper.py       # RAG-specific helpers
├── orchestrator.py                   # Main orchestration logic
├── plotting_and_reporting.py         # Visualization utilities
├── pricing_calculator.py             # Cost analysis tools
├── text_extractor_and_summarizer.py  # Text processing utilities
└── requirements.txt
```

## Features

- Model performance evaluation
- Token usage tracking and analysis
- Cost calculation and optimization
- RAG (Retrieval-Augmented Generation) evaluation
- Automated reporting and visualization
- Knowledge base management
- Text extraction and summarization
- Comparative model analysis

## Prerequisites

- Python 3.12+
- AWS Account with Bedrock access
- AWS credentials configured

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aws-samples/AWS-First-GenAI-Journey.git
cd AWS-First-GenAI-Journey/Amazon-Bedrock-Model-Evaluator
```

2. Create and activate a virtual environment:
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

Create a `.env` file in the project directory:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## Running the Application

```bash
streamlit run app.py
```

## Usage Examples

### Basic Model Evaluation

```python
from evaluation_steps import evaluate_model

results = evaluate_model(
    model_name="model-name",
    test_cases=test_dataset,
    metrics=["accuracy", "latency", "token_usage"]
)
```

### Token Usage Analysis

```python
from AnthropicTokenCounter import count_tokens

token_count = count_tokens(text="Your text here", model="claude-3")
```

### Cost Calculation

```python
from pricing_calculator import calculate_cost

estimated_cost = calculate_cost(
    token_count=1000,
    model_name="model-name",
    operation_type="inference"
)
```

### Generate Reports

```python
from plotting_and_reporting import generate_report

report = generate_report(evaluation_results=results, report_type="comprehensive")
```

## Evaluation Metrics

- Response Quality
- Latency
- Token Efficiency
- Cost Effectiveness
- Knowledge Accuracy
- RAG Performance
- Error Rates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
