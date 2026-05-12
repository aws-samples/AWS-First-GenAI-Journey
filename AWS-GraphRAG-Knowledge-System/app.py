import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import os
from graph_builder import extract_entities, build_graph, graph_search, generate_answer

st.set_page_config(page_title="GraphRAG Knowledge System", layout="wide")
st.title("🔗 GraphRAG Knowledge System")

if "graph" not in st.session_state:
    st.session_state.graph = nx.DiGraph()
if "extracted" not in st.session_state:
    st.session_state.extracted = {"entities": [], "relationships": []}

# Document Upload
st.sidebar.header("📄 Upload Document")
uploaded = st.sidebar.file_uploader("Upload a text file", type=["txt", "md"])

if uploaded and st.sidebar.button("Extract Entities"):
    text = uploaded.read().decode("utf-8")
    with st.spinner("Extracting entities via Bedrock..."):
        result = extract_entities(text)
        st.session_state.extracted["entities"].extend(result.get("entities", []))
        st.session_state.extracted["relationships"].extend(result.get("relationships", []))
        st.session_state.graph = build_graph(st.session_state.extracted)
    st.sidebar.success(
        f"Extracted {len(result.get('entities', []))} entities, "
        f"{len(result.get('relationships', []))} relationships"
    )

# Graph Visualization
st.header("🕸️ Knowledge Graph")
G = st.session_state.graph
if G.number_of_nodes() > 0:
    net = Network(height="450px", width="100%", directed=True)
    for node, data in G.nodes(data=True):
        net.add_node(node, label=node, title=data.get("type", ""))
    for s, t, data in G.edges(data=True):
        net.add_edge(s, t, label=data.get("relation", ""))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w") as f:
        net.save_graph(f.name)
        st.components.v1.html(open(f.name).read(), height=500)
        os.unlink(f.name)
else:
    st.info("Upload a document and extract entities to build the knowledge graph.")

# Query
st.header("❓ Query with Graph-Enhanced RAG")
query = st.text_input("Ask a question about your documents")
if query and st.button("Get Answer"):
    with st.spinner("Searching graph and generating answer..."):
        subgraph = graph_search(G, query)
        answer = generate_answer(subgraph, query)
    st.subheader("Answer")
    st.write(answer)
    if subgraph.number_of_edges() > 0:
        with st.expander("Relevant subgraph context"):
            for s, t, d in subgraph.edges(data=True):
                st.write(f"- {s} --[{d.get('relation', '')}]--> {t}")

# Stats
st.sidebar.markdown("---")
st.sidebar.metric("Nodes", G.number_of_nodes())
st.sidebar.metric("Edges", G.number_of_edges())
