from typing import List, Dict, Any

from src.state import AppState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Static knowledge for enriching diagnoses
_DISEASE_META: Dict[str, Dict[str, Any]] = {
    "STEMI": {
        "recommended_tests": ["ECG", "Troponin"],
        "initial_management": ["Aspirin", "PCI pathway", "抗凝治疗"],
    },
    "主动脉夹层": {
        "recommended_tests": ["CT血管造影", "胸部X线"],
        "initial_management": ["控制血压", "镇痛", "急诊外科会诊"],
    },
    "肺栓塞": {
        "recommended_tests": ["D-dimer", "CT肺动脉造影", "超声心动图"],
        "initial_management": ["低分子肝素", "肝素", "溶栓（大面积）"],
    },
}

_DISCLAIMER = "该结果用于教学与演示，不构成临床建议。"


def run_reasoner(state: AppState) -> AppState:
    """Synthesize doc_hits and graph_hits to produce final_answer.

    Uses rule-based scoring (no LLM): each disease gets a score from graph
    candidate_diseases plus doc_hits matching. Produces structured JSON output.
    """
    doc_hits: List[Dict[str, Any]] = state.get("doc_hits", [])
    graph_hits: List[Dict[str, Any]] = state.get("graph_hits", [])
    candidate_diseases: List[Dict[str, Any]] = state.get("candidate_diseases", [])
    parsed_case: Dict[str, Any] = state.get("parsed_case", {})
    logs: List[str] = list(state.get("logs", []))

    logger.info("Running reasoner")
    logs.append("reasoner: started")

    # Build disease score map from graph candidates
    disease_scores: Dict[str, float] = {}
    disease_evidence: Dict[str, List[str]] = {}
    for cand in candidate_diseases:
        name = cand["disease"]
        disease_scores[name] = float(cand["score"])
        disease_evidence[name] = list(cand.get("matched_evidence", []))

    # Boost score from doc hits
    for hit in doc_hits:
        disease = hit.get("disease", "")
        if disease:
            disease_scores[disease] = disease_scores.get(disease, 0.0) + hit.get(
                "_score", 0
            ) * 0.5

    # Collect citations per disease from doc hits
    disease_citations: Dict[str, List[str]] = {}
    for hit in doc_hits:
        disease = hit.get("disease", "")
        source = hit.get("source", "")
        if disease and source:
            disease_citations.setdefault(disease, []).append(source)

    # Normalize scores to confidence (0-1)
    max_score = max(disease_scores.values(), default=1.0) or 1.0

    # Build candidate diagnoses list sorted by score
    sorted_diseases = sorted(
        disease_scores.items(), key=lambda x: x[1], reverse=True
    )

    candidate_diagnoses = []
    for rank, (name, score) in enumerate(sorted_diseases[:3], start=1):
        meta = _DISEASE_META.get(name, {})
        confidence = round(min(score / max_score, 1.0), 2)
        candidate_diagnoses.append(
            {
                "name": name,
                "rank": rank,
                "confidence": confidence,
                "supporting_evidence": disease_evidence.get(name, []),
                "against_evidence": [],
                "recommended_tests": meta.get("recommended_tests", []),
                "initial_management": meta.get("initial_management", []),
                "citations": list(dict.fromkeys(disease_citations.get(name, []))),
            }
        )

    # Build case summary
    age = parsed_case.get("age", "未知")
    gender = parsed_case.get("gender", "未知")
    chief = parsed_case.get("chief_complaint", "")
    case_summary = f"{age}岁{gender}性患者，主诉：{chief}。"

    top_name = candidate_diagnoses[0]["name"] if candidate_diagnoses else "不明"
    next_steps = [
        f"优先考虑 {top_name}，立即完善相关检查",
        "监测生命体征，建立静脉通路",
        "必要时紧急会诊",
    ]

    final_answer: Dict[str, Any] = {
        "case_summary": case_summary,
        "candidate_diagnoses": candidate_diagnoses,
        "next_steps": next_steps,
        "notes": _DISCLAIMER,
    }

    logs.append(
        f"reasoner: top diagnosis={top_name}, "
        f"{len(candidate_diagnoses)} candidates"
    )

    return {**state, "final_answer": final_answer, "logs": logs}
