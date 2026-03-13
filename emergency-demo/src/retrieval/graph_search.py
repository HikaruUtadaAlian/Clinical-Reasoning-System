from typing import List, Dict, Any, Tuple

from src.utils.io import load_json


def load_graph(filepath: str) -> Dict[str, Any]:
    """Load the knowledge graph from a JSON file."""
    return load_json(filepath)


def search_graph(
    query_terms: List[str],
    graph: Dict[str, Any],
    top_k: int = 3,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Find disease nodes reachable from symptom/finding/sign/test nodes
    that match query_terms.

    Returns:
        hits: list of matched non-disease node dicts
        candidate_diseases: ranked list of disease dicts with scores
    """
    nodes: List[Dict[str, Any]] = graph.get("nodes", [])
    edges: List[Dict[str, Any]] = graph.get("edges", [])

    # Index nodes by id for quick lookup
    node_by_id: Dict[str, Dict[str, Any]] = {n["id"]: n for n in nodes}

    # Find non-disease nodes whose label matches any query term
    matched_nodes: List[Dict[str, Any]] = []
    for node in nodes:
        if node.get("type") == "disease":
            continue
        label = node.get("label", "")
        if any(term and term in label for term in query_terms):
            matched_nodes.append(node)

    matched_ids = {n["id"] for n in matched_nodes}

    # Walk edges: disease --edge--> matched_node  (disease has_symptom/sign/finding/requires_test ...)
    disease_scores: Dict[str, int] = {}
    disease_evidence: Dict[str, List[str]] = {}

    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        source_node = node_by_id.get(source, {})
        if source_node.get("type") == "disease" and target in matched_ids:
            disease_scores[source] = disease_scores.get(source, 0) + 1
            disease_evidence.setdefault(source, []).append(target)

    # Build candidate list sorted by score
    candidates = []
    for disease_id, score in sorted(
        disease_scores.items(), key=lambda x: x[1], reverse=True
    ):
        disease_node = node_by_id.get(disease_id, {})
        candidates.append(
            {
                "disease": disease_id,
                "label": disease_node.get("label", disease_id),
                "score": score,
                "matched_evidence": disease_evidence.get(disease_id, []),
            }
        )

    return matched_nodes[:top_k], candidates[:top_k]
