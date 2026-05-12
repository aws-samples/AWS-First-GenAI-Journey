# AWS Agent Evaluator

A framework for evaluating AI agent performance using Strands Evals patterns.

## Overview

This tool lets you define test scenarios, run an agent against them, and view pass/fail results with accuracy, relevance, and safety metrics.

## Project Structure

- `app.py` - Streamlit UI for running evaluations interactively
- `eval_runner.py` - Core evaluation logic with scoring functions
- `scenarios.json` - Test scenarios with inputs, expected outputs, and tags

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Run the Streamlit app

```bash
streamlit run app.py
```

### Use programmatically

```python
from eval_runner import load_scenarios, run_evaluation

scenarios = load_scenarios()
result = run_evaluation(scenarios[0], "Your agent response here")
print(result)
```

## Scoring

- **Accuracy** (40%) - Keyword overlap between response and expected output
- **Relevance** (30%) - How well the response relates to the input query
- **Safety** (30%) - Absence of harmful content patterns

A scenario passes when the weighted overall score is >= 0.5.

## Adding Scenarios

Edit `scenarios.json` to add new test cases with `name`, `input`, `expected_output`, and `tags` fields.
