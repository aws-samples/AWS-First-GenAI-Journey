import json
import boto3
import networkx as nx

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "anthropic.claude-sonnet-4-6"


def converse(prompt):
    resp = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 4096},
    )
    return resp["output"]["message"]["content"][0]["text"]


def extract_entities(text):
    prompt = (
        "Extract entities and relationships from the following text. "
        "Return JSON with format: {\"entities\": [{\"name\": str, \"type\": str}], "
        "\"relationships\": [{\"source\": str, \"target\": str, \"relation\": str}]}\n\n"
        "Only return valid JSON, no other text.\n\nText:\n" + text
    )
    raw = converse(prompt)
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {"entities": [], "relationships": []}


def build_graph(extracted):
    G = nx.DiGraph()
    for ent in extracted.get("entities", []):
        G.add_node(ent["name"], type=ent.get("type", "unknown"))
    for rel in extracted.get("relationships", []):
        G.add_edge(rel["source"], rel["target"], relation=rel.get("relation", ""))
    return G


def graph_search(G, query):
    query_lower = query.lower()
    matched = [n for n in G.nodes if query_lower in n.lower()]
    subgraph_nodes = set(matched)
    for node in matched:
        subgraph_nodes.update(G.predecessors(node))
        subgraph_nodes.update(G.successors(node))
    if not subgraph_nodes:
        return G
    return G.subgraph(subgraph_nodes)


def generate_answer(G, query):
    edges = list(G.edges(data=True))
    context_parts = [f"{s} --[{d.get('relation','')}]--> {t}" for s, t, d in edges]
    context = "\n".join(context_parts) if context_parts else "No graph context available."
    prompt = (
        f"Using the following knowledge graph context, answer the question.\n\n"
        f"Graph context:\n{context}\n\nQuestion: {query}"
    )
    return converse(prompt)
