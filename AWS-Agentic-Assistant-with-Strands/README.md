# AWS Agentic Assistant with Strands SDK

An AI agent powered by [Strands Agents SDK](https://strandsagents.com/) and Amazon Bedrock that can use tools, search AWS documentation via MCP, and generate reports.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Strands Agent Loop                  │
│                                                 │
│  User Input → LLM Reasoning → Tool Selection    │
│       ↑              ↓                          │
│       └──── Result ← Tool Execution            │
│                                                 │
├─────────────────────────────────────────────────┤
│  Tools:                                         │
│  • save_report    - Save markdown reports       │
│  • list_reports   - List saved reports          │
│  • calculate      - Safe math evaluation        │
│  • AWS MCP Server - Query AWS documentation     │
├─────────────────────────────────────────────────┤
│  Guardrails (Hooks):                            │
│  • safety_guard   - Block destructive ops       │
│  • log_tool_calls - Observability logging       │
├─────────────────────────────────────────────────┤
│  Model: Amazon Bedrock (Claude Sonnet 4.6)      │
└─────────────────────────────────────────────────┘
```

## Features

- **Multi-tool Agent** — Reasons about which tools to use and chains them together
- **MCP Integration** — Connect to AWS documentation via Model Context Protocol
- **Safety Hooks** — Blocks destructive operations before execution
- **Conversation Memory** — Sliding window keeps context manageable
- **Streamlit UI** — Chat interface for interactive use
- **CLI Mode** — Terminal-based interaction

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials (Bedrock access required)
export AWS_REGION=us-east-1

# Optional: Enable MCP for AWS documentation search
export USE_MCP=true
```

## Usage

### CLI Mode
```bash
python agent.py
```

### Streamlit UI
```bash
streamlit run app.py
```

### Example Interactions

```
You: What is Amazon Bedrock AgentCore and how does it help with agent security?
Assistant: [searches docs, generates comprehensive answer with citations]

You: Calculate the monthly cost of 1M Bedrock API calls at $0.003 per 1K input tokens
Assistant: [uses calculate tool] Monthly cost = $3,000

You: Save a report summarizing Bedrock pricing
Assistant: [generates report, saves to reports/Bedrock_Pricing.md]
```

## Project Structure

```
├── agent.py          # Core agent with tools and hooks
├── app.py            # Streamlit chat UI
├── requirements.txt  # Dependencies
└── reports/          # Generated reports (auto-created)
```

## Key Concepts (2026 Patterns)

| Pattern | Implementation |
|---------|---------------|
| **Model-driven agents** | Strands SDK — LLM decides tool usage |
| **MCP tools** | AWS documentation server via stdio |
| **Safety hooks** | BeforeToolCallEvent blocks dangerous ops |
| **Observability** | AfterToolCallEvent logs all tool calls |
| **Context management** | SlidingWindowConversationManager |
| **Structured output** | Pydantic models for typed responses |

## References

- [Strands Agents SDK](https://strandsagents.com/)
- [AWS MCP Servers](https://aws.amazon.com/solutions/guidance/vibe-coding-with-aws-mcp-servers/)
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/best-practices.html)
- [OWASP Top 10 for Agentic AI (2026)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
