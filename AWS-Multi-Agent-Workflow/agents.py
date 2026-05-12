"""Multi-agent pipeline: Researcher → Writer → Reviewer using Strands agent-as-tool pattern."""

from strands import Agent
from strands.agent.tool import tool

# Define specialized agents
researcher = Agent(
    system_prompt=(
        "You are a research specialist. Given a topic, provide key facts, "
        "statistics, and insights in a structured bullet-point format. "
        "Be concise and factual."
    )
)

writer = Agent(
    system_prompt=(
        "You are a professional writer. Given research notes, write a clear, "
        "engaging article of 3-4 paragraphs. Use a professional tone."
    )
)

reviewer = Agent(
    system_prompt=(
        "You are an editorial reviewer. Review the article for clarity, "
        "accuracy, grammar, and engagement. Provide specific feedback "
        "and a final improved version."
    )
)


# Wrap agents as tools for the orchestrator
@tool
def research_topic(topic: str) -> str:
    """Research a topic and return structured findings."""
    result = researcher(f"Research this topic: {topic}")
    return str(result)


@tool
def write_article(research_notes: str) -> str:
    """Write an article based on research notes."""
    result = writer(f"Write an article based on these notes:\n{research_notes}")
    return str(result)


@tool
def review_article(article: str) -> str:
    """Review and improve an article."""
    result = reviewer(f"Review and improve this article:\n{article}")
    return str(result)


# Orchestrator agent that coordinates the pipeline
orchestrator = Agent(
    system_prompt=(
        "You are a content pipeline orchestrator. Given a topic, you must: "
        "1) Use research_topic to gather information, "
        "2) Use write_article to create an article from the research, "
        "3) Use review_article to get the final polished version. "
        "Execute all three steps in order and present each step's output."
    ),
    tools=[research_topic, write_article, review_article],
)


def run_pipeline(topic: str) -> dict:
    """Run the full pipeline and return intermediate results."""
    research = str(researcher(f"Research this topic: {topic}"))
    article = str(writer(f"Write an article based on these notes:\n{research}"))
    review = str(reviewer(f"Review and improve this article:\n{article}"))
    return {"research": research, "article": article, "review": review}
