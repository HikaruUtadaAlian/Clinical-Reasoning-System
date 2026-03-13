import re
from typing import List

from src.state import AppState
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Predefined clinical terms to match against case text
KNOWN_SYMPTOMS = [
    "胸痛", "胸背部撕裂样疼痛", "呼吸困难", "出汗", "心动过速",
    "晕厥", "心悸", "咯血", "发热", "恶心", "呕吐",
]
KNOWN_SIGNS = [
    "双上肢血压不一致", "血压下降", "心率加快", "颈静脉怒张",
]
KNOWN_FINDINGS = [
    "ST段抬高", "D-dimer升高", "Troponin升高", "ECG异常",
]
KNOWN_TESTS = [
    "ECG", "Troponin", "CT血管造影", "D-dimer", "心电图",
]


def run_case_parser(state: AppState) -> AppState:
    """Parse the case text to extract structured information.

    Extracts: age, gender, chief_complaint, symptoms, signs, findings.
    Generates query_terms list for retrieval.
    Uses simple rule-based parsing (no LLM needed for MVP).
    """
    case_text: str = state.get("case_text", "")
    logs: List[str] = list(state.get("logs", []))

    logger.info("Parsing case text")
    logs.append("case_parser: started")

    # Extract age
    age = None
    age_match = re.search(r"(\d+)岁", case_text)
    if age_match:
        age = int(age_match.group(1))

    # Extract gender
    gender = None
    if "男" in case_text:
        gender = "男"
    elif "女" in case_text:
        gender = "女"

    # Match known clinical terms
    symptoms = [s for s in KNOWN_SYMPTOMS if s in case_text]
    signs = [s for s in KNOWN_SIGNS if s in case_text]
    findings = [s for s in KNOWN_FINDINGS if s in case_text]
    tests = [t for t in KNOWN_TESTS if t in case_text]

    # Chief complaint: first clause up to first comma or period
    chief_complaint = re.split(r"[，。,.]", case_text)[0].strip() if case_text else ""

    parsed_case = {
        "age": age,
        "gender": gender,
        "chief_complaint": chief_complaint,
        "symptoms": symptoms,
        "signs": signs,
        "findings": findings,
        "tests_mentioned": tests,
    }

    # Build query terms: unique non-empty terms from all clinical categories
    query_terms: List[str] = list(
        dict.fromkeys(symptoms + signs + findings + tests)
    )
    # Also add any explicit short tokens from the text (2-6 char Chinese tokens)
    for token in re.findall(r"[\u4e00-\u9fff]{2,6}", case_text):
        if token not in query_terms:
            query_terms.append(token)

    logs.append(
        f"case_parser: age={age}, gender={gender}, "
        f"symptoms={symptoms}, signs={signs}, findings={findings}"
    )

    return {
        **state,
        "parsed_case": parsed_case,
        "query_terms": query_terms,
        "logs": logs,
    }
