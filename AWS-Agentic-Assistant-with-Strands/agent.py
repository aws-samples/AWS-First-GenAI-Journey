"""
AWS Agentic Assistant with Strands SDK + MCP (2026)

A multi-tool AI agent that can:
- Query AWS resources via MCP
- Search and summarize documents
- Perform calculations and data analysis
- Save reports to disk

Uses: Strands Agents SDK, Amazon Bedrock, MCP Protocol
"""

import os
from pathlib import Path
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent
from strands.agent import SlidingWindowConversationManager
from mcp import stdio_client, StdioServerParameters


# ---------------------------------------------------------------------------
# Custom Tools
# ---------------------------------------------------------------------------

@tool
def save_report(title: str, content: str) -> str:
    """Save a research report as markdown file."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"{title.replace(' ', '_')}.md"
    path.write_text(content)
    return f"Report saved to {path}"


@tool
def list_reports() -> str:
    """List all saved reports."""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        return "No reports found."
    files = list(reports_dir.glob("*.md"))
    if not files:
        return "No reports found."
    return "\n".join(f"- {f.name}" for f in files)


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: Only numeric expressions allowed."
    try:
        result = eval(expression)  # noqa: S307 - input is sanitized above
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Hooks (Guardrails)
# ---------------------------------------------------------------------------

BLOCKED_ACTIONS = ["rm ", "delete", "drop ", "format "]


def safety_guard(event: BeforeToolCallEvent):
    """Block dangerous operations."""
    input_str = str(event.tool_use.get("input", "")).lower()
    if any(action in input_str for action in BLOCKED_ACTIONS):
        event.cancel_tool = "Blocked: potentially destructive operation."


def log_tool_calls(event: AfterToolCallEvent):
    """Log tool executions for observability."""
    name = event.tool_use.get("name", "unknown")
    status = event.result.get("status", "unknown")
    print(f"  [tool] {name} → {status}")


# ---------------------------------------------------------------------------
# MCP Integration (AWS services via MCP server)
# ---------------------------------------------------------------------------

def create_aws_mcp_client():
    """Create MCP client for AWS services (requires awslabs.aws-mcp-server)."""
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server"],
        )
    ))


# ---------------------------------------------------------------------------
# Agent Factory
# ---------------------------------------------------------------------------

def create_agent(use_mcp: bool = False) -> Agent:
    """Create the agentic assistant.

    Args:
        use_mcp: Whether to include AWS MCP tools (requires MCP server installed)
    """
    tools = [save_report, list_reports, calculate]

    if use_mcp:
        try:
            aws_mcp = create_aws_mcp_client()
            tools.append(aws_mcp)
        except Exception as e:
            print(f"Warning: MCP client not available ({e}). Running without AWS tools.")

    agent = Agent(
        system_prompt=(
            "You are an AWS cloud assistant powered by Amazon Bedrock. "
            "You help users understand AWS services, analyze architectures, "
            "and generate reports. Use your tools to search documentation, "
            "perform calculations, and save findings. "
            "Always cite sources when providing AWS information."
        ),
        model="bedrock/anthropic.claude-sonnet-4-6",
        tools=tools,
        hooks=[safety_guard, log_tool_calls],
        conversation_manager=SlidingWindowConversationManager(window_size=20),
    )
    return agent


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def main():
    """Interactive CLI for the agentic assistant."""
    use_mcp = os.environ.get("USE_MCP", "false").lower() == "true"
    agent = create_agent(use_mcp=use_mcp)

    print("🤖 AWS Agentic Assistant (Strands SDK + Bedrock)")
    print("   Type 'quit' to exit, 'reports' to list saved reports\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "reports":
            print(list_reports())
            continue

        result = agent(user_input)
        print(f"\nAssistant: {result}\n")


if __name__ == "__main__":
    main()
