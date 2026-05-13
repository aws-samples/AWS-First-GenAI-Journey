# GenAI Observability Dashboard

Real-time monitoring dashboard for GenAI application metrics built with Streamlit.

## Features

- **Token Usage**: Daily input/output token consumption (stacked bar chart)
- **Latency Monitoring**: P50 and P99 latency trends over time
- **Cost Breakdown**: Per-model cost analysis (pie chart)
- **Guardrail Blocks**: Block rate tracking for content safety guardrails

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

- `app.py` — Streamlit dashboard with Plotly charts
- `metrics.py` — Data layer (CloudWatch integration or mock data for demo)

## Data Source

By default, the dashboard generates sample data for demonstration.
To connect to CloudWatch, update `fetch_metrics()` in `metrics.py` with your
CloudWatch namespace and metric names.

## Requirements

- Python 3.9+
- AWS credentials configured (for CloudWatch integration)
