from typing import TypedDict, List, Dict, Any


class AppState(TypedDict, total=False):
    case_text: str
    parsed_case: Dict[str, Any]
    query_terms: List[str]
    doc_hits: List[Dict[str, Any]]
    graph_hits: List[Dict[str, Any]]
    candidate_diseases: List[Dict[str, Any]]
    final_answer: Dict[str, Any]
    logs: List[str]
