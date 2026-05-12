# GraphRAG Knowledge System

A Graph-based Retrieval Augmented Generation system that extracts entities and relationships from documents, builds a knowledge graph, and uses it for enhanced question answering.

## Architecture

1. **Document Upload** - Upload text documents via Streamlit UI
2. **Entity Extraction** - Uses Amazon Bedrock Converse API (Claude 3 Sonnet) to extract entities and relationships as structured JSON
3. **Knowledge Graph** - Builds a directed graph using NetworkX from extracted entities/relationships
4. **Graph-Enhanced RAG** - Queries find relevant subgraphs, which provide context for answer generation

## Prerequisites

- Python 3.9+
- AWS credentials configured with Bedrock access
- Access to `anthropic.claude-3-sonnet-20240229-v1:0` model in us-east-1

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

1. Upload a `.txt` or `.md` file in the sidebar
2. Click "Extract Entities" to build the knowledge graph
3. View the interactive graph visualization
4. Ask questions in the query section for graph-enhanced answers

## Project Structure

```
├── app.py              # Streamlit application
├── graph_builder.py    # Core logic (extraction, graph, search, generation)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## How It Works

- **extract_entities()** - Prompts Bedrock to return structured JSON with entities and relationships
- **build_graph()** - Creates a NetworkX DiGraph from the extracted data
- **graph_search()** - Finds relevant subgraph nodes matching the query
- **generate_answer()** - Combines graph context with Bedrock to produce answers

## License

MIT
