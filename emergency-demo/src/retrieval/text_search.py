from typing import List, Dict, Any

from src.utils.io import load_jsonl


def load_chunks(filepath: str) -> List[Dict[str, Any]]:
    """Load document chunks from a JSONL file."""
    return load_jsonl(filepath)


def search_chunks(
    query_terms: List[str],
    chunks: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Keyword-based chunk search.

    Scores each chunk by counting how many query_terms appear in its text,
    then returns the top_k highest-scoring chunks.
    """
    scored = []
    for chunk in chunks:
        text = chunk.get("text", "")
        score = sum(1 for term in query_terms if term and term in text)
        if score > 0:
            scored.append({**chunk, "_score": score})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:top_k]
