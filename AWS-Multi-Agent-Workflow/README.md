# Multi-Agent Content Pipeline

A multi-agent system using the **Researcher → Writer → Reviewer** pattern built with [Strands Agents SDK](https://github.com/strands-agents/sdk-python).

## Architecture

```
User Topic → Orchestrator Agent
                ├── 1. Researcher Agent (gathers facts)
                ├── 2. Writer Agent (creates article)
                └── 3. Reviewer Agent (polishes output)
```

Each agent is wrapped as a tool using the Strands **agent-as-tool** pattern, allowing the orchestrator to coordinate the pipeline.

## Prerequisites

- Python 3.10+
- AWS credentials configured (for Amazon Bedrock)
- Access to a Bedrock model (default: Claude)

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit UI for topic input and pipeline output |
| `agents.py` | Agent definitions and orchestrator with agent-as-tool pattern |
| `requirements.txt` | Python dependencies |

## How It Works

1. User enters a topic in the Streamlit interface
2. The pipeline runs three specialized agents sequentially
3. Each agent's output feeds into the next stage
4. All intermediate results are displayed in the UI
