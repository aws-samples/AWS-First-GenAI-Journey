import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_metrics(days=7):
    """Fetch metrics from CloudWatch or generate sample data for demo."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
    return pd.DataFrame({
        "date": dates,
        "input_tokens": np.random.randint(5000, 50000, days),
        "output_tokens": np.random.randint(2000, 20000, days),
        "latency_p50": np.random.uniform(0.3, 1.2, days),
        "latency_p99": np.random.uniform(2.0, 5.0, days),
        "guardrail_total": np.random.randint(100, 500, days),
        "guardrail_blocked": np.random.randint(5, 50, days),
    })

def calculate_costs(df):
    """Calculate cost breakdown by model (per 1K tokens pricing)."""
    models = ["Claude 3.5 Sonnet", "Claude 3 Haiku", "Titan Text"]
    prices_input = [0.003, 0.00025, 0.0003]
    prices_output = [0.015, 0.00125, 0.0015]
    total_input = df["input_tokens"].sum()
    total_output = df["output_tokens"].sum()
    splits = [0.5, 0.3, 0.2]
    costs = []
    for model, pi, po, split in zip(models, prices_input, prices_output, splits):
        cost = (total_input * split / 1000 * pi) + (total_output * split / 1000 * po)
        costs.append({"model": model, "cost": round(cost, 2)})
    return pd.DataFrame(costs)
