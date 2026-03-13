import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.case_parser import run_case_parser


def _run(text: str):
    state = {"case_text": text, "logs": []}
    return run_case_parser(state)


def test_extracts_age():
    result = _run("65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。")
    assert result["parsed_case"]["age"] == 65


def test_extracts_gender_male():
    result = _run("58岁男性，突发胸背部撕裂样疼痛。")
    assert result["parsed_case"]["gender"] == "男"


def test_extracts_gender_female():
    result = _run("42岁女性，突发胸痛伴呼吸困难，心动过速，D-dimer升高。")
    assert result["parsed_case"]["gender"] == "女"


def test_query_terms_nonempty():
    result = _run("65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。")
    assert len(result["query_terms"]) > 0


def test_symptoms_extracted():
    result = _run("患者胸痛、出汗明显。")
    assert "胸痛" in result["parsed_case"]["symptoms"]
    assert "出汗" in result["parsed_case"]["symptoms"]
