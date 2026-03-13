from pathlib import Path
from typing import List

from src.state import AppState
from src.retrieval.text_search import load_chunks, search_chunks
from src.utils.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def run_doc_retriever(state: AppState) -> AppState:
    """Retrieve relevant document chunks based on query_terms."""
    query_terms: List[str] = state.get("query_terms", [])
    logs: List[str] = list(state.get("logs", []))

    logger.info("Running doc retriever with %d query terms", len(query_terms))
    logs.append(f"doc_retriever: query_terms={query_terms[:5]}")

    chunks_path = DATA_DIR / "chunks.jsonl"
    chunks = load_chunks(str(chunks_path))
    doc_hits = search_chunks(query_terms, chunks, top_k=5)

    logs.append(f"doc_retriever: found {len(doc_hits)} hits")

    return {**state, "doc_hits": doc_hits, "logs": logs}
