# AWS GenAI Cost Optimizer

A tool to analyze and optimize AWS Bedrock/GenAI costs using intelligent model routing.

## How It Works

1. **Upload** your Bedrock usage logs (CSV format)
2. **Analyze** cost patterns across your queries
3. **Get recommendations** for cheaper models based on query complexity
4. **See savings** estimates with optimized routing

## Model Routing Strategy

| Complexity | Model | Use Case |
|-----------|-------|----------|
| Simple | Claude Haiku | Short, factual queries |
| Medium | Claude Sonnet | Moderate analysis tasks |
| Complex | Claude Opus | Deep reasoning, multi-step tasks |

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## CSV Format

Your usage log CSV should have these columns:

| Column | Description |
|--------|-------------|
| query | The text of the query sent |
| model | Model used (haiku/sonnet/opus) |
| input_tokens | Number of input tokens |
| output_tokens | Number of output tokens |

## Architecture

- `app.py` - Streamlit UI for uploading logs and viewing results
- `router.py` - Query complexity classifier and cost calculator

## License

MIT
