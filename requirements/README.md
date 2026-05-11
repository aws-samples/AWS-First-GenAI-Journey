# Shared Requirements Layers

Centralized dependency management for all projects in this repo.
When a CVE fix or version bump is needed for a shared package, update **one file here** — all projects that reference it pick up the change automatically.

## Layer hierarchy

```
base.txt          ← AWS SDK, Streamlit, Pillow, requests, urllib3
  └── langchain.txt     ← + LangChain stack, pypdf
        └── langchain-ml.txt  ← + transformers, torch, faiss, opencv, numpy
  └── ml.txt            ← + transformers, torch, faiss, opencv, numpy (without LangChain)
```

## Which layer to use

| Your project needs | Use |
|--------------------|-----|
| Just boto3 + streamlit | `base.txt` |
| RAG / agents with LangChain | `langchain.txt` |
| Vision / ML only | `ml.txt` |
| LangChain + vision/ML | `langchain-ml.txt` |

## Usage in a project's requirements.txt

```
-r ../requirements/langchain-ml.txt

# Project-specific extras
some-extra-package==1.2.3
```

## Key packages and their CVE history

| Package | Current | Notes |
|---------|---------|-------|
| `Pillow` | 12.1.0 | CVE-2026-42311 fixed in 12.1.0 |
| `tornado` | 6.4.2 | Security fix vs 6.4.1 |
| `urllib3` | 2.3.0 | Upgrade from 1.x branch |
| `boto3` | 1.35.58 | Pinned for stability |
