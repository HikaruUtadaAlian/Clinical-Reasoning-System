from pathlib import Path
from typing import List

from src.state import AppState
from src.retrieval.graph_search import load_graph, search_graph
from src.utils.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def run_graph_retriever(state: AppState) -> AppState:
    """Retrieve graph nodes and candidate diseases based on query_terms."""
    query_terms: List[str] = state.get("query_terms", [])
    logs: List[str] = list(state.get("logs", []))

    logger.info("Running graph retriever with %d query terms", len(query_terms))
    logs.append(f"graph_retriever: query_terms={query_terms[:5]}")

    graph_path = DATA_DIR / "graph.json"
    graph = load_graph(str(graph_path))
    graph_hits, candidate_diseases = search_graph(query_terms, graph, top_k=3)

    logs.append(
        f"graph_retriever: {len(graph_hits)} hits, "
        f"{len(candidate_diseases)} candidate diseases"
    )

    return {
        **state,
        "graph_hits": graph_hits,
        "candidate_diseases": candidate_diseases,
        "logs": logs,
    }
