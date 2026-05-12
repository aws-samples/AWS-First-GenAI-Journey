"""Intelligent model router for GenAI cost optimization."""

# Cost per 1K tokens (input/output) in USD
MODEL_COSTS = {
    "haiku": {"input": 0.00025, "output": 0.00125},
    "sonnet": {"input": 0.003, "output": 0.015},
    "opus": {"input": 0.015, "output": 0.075},
}

COMPLEXITY_THRESHOLDS = {"simple": 50, "medium": 200}


def classify_complexity(query: str) -> str:
    """Classify query complexity based on token length and indicators."""
    words = len(query.split())
    complex_indicators = ["analyze", "compare", "explain in detail", "summarize", "multi-step"]
    if words < COMPLEXITY_THRESHOLDS["simple"] and not any(k in query.lower() for k in complex_indicators):
        return "simple"
    if words < COMPLEXITY_THRESHOLDS["medium"]:
        return "medium"
    return "complex"


def route_model(complexity: str) -> str:
    """Route to appropriate model based on complexity."""
    return {"simple": "haiku", "medium": "sonnet", "complex": "opus"}[complexity]


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a given model and token counts."""
    costs = MODEL_COSTS[model]
    return (input_tokens / 1000) * costs["input"] + (output_tokens / 1000) * costs["output"]


def estimate_savings(rows: list[dict]) -> list[dict]:
    """Estimate savings by routing each query to the optimal model."""
    results = []
    for row in rows:
        query = row.get("query", "")
        input_tokens = int(row.get("input_tokens", 0))
        output_tokens = int(row.get("output_tokens", 0))
        original_model = row.get("model", "opus").lower()

        complexity = classify_complexity(query)
        recommended = route_model(complexity)
        original_cost = calculate_cost(original_model, input_tokens, output_tokens)
        optimized_cost = calculate_cost(recommended, input_tokens, output_tokens)

        results.append({
            "query": query[:80],
            "original_model": original_model,
            "recommended_model": recommended,
            "complexity": complexity,
            "original_cost": original_cost,
            "optimized_cost": optimized_cost,
            "savings": original_cost - optimized_cost,
        })
    return results
