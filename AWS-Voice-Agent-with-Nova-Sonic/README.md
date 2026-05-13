# 🎙️ AWS Voice Agent with Amazon Nova Sonic

A Voice AI Agent powered by **Amazon Nova Sonic** (bidirectional streaming voice model) and the **Strands Agents SDK**.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│  Microphone │────▶│  Agent.py   │────▶│  Amazon Nova     │
│  (input)    │     │  (Strands)  │     │  Sonic (Bedrock) │
└─────────────┘     └─────────────┘     └──────────────────┘
                          │                       │
                          ▼                       ▼
                    ┌─────────────┐     ┌──────────────────┐
                    │  Tools      │     │  Audio Response   │
                    │  - weather  │     │  (streaming)      │
                    │  - search   │     └──────────────────┘
                    │  - reminder │
                    └─────────────┘
```

## Components

- **agent.py** — Core voice agent with Nova Sonic streaming and tool functions
- **app.py** — Streamlit web UI with audio input/output and chat history
- **Tools** — `get_weather`, `search_knowledge`, `set_reminder`

## Prerequisites

- Python 3.10+
- AWS account with Bedrock access (Nova Sonic model enabled)
- AWS credentials configured (`~/.aws/credentials` or environment variables)

## Setup

```bash
# Clone and navigate
cd AWS-Voice-Agent-with-Nova-Sonic

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Mode (direct microphone)

```bash
python agent.py
```

### Web UI (Streamlit)

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser, click the microphone to record, and interact with the agent.

## Configuration

Set your AWS region in `agent.py` (default: `us-east-1`). Ensure the Nova Sonic model is enabled in your Bedrock console.

## License

MIT
