import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph_workflow import run_workflow

CASE_A = "65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。"
CASE_B = "58岁男性，突发胸背部撕裂样疼痛，双上肢血压不一致。"
CASE_C = "42岁女性，突发胸痛伴呼吸困难，心动过速，D-dimer升高。"


def test_workflow_returns_final_answer():
    result = run_workflow(CASE_A)
    assert isinstance(result, dict)
    assert "candidate_diagnoses" in result


def test_workflow_case_a_stemi():
    result = run_workflow(CASE_A)
    diagnoses = result.get("candidate_diagnoses", [])
    assert len(diagnoses) > 0
    top = diagnoses[0]["name"]
    assert top == "STEMI", f"Expected STEMI as top diagnosis, got {top}"


def test_workflow_case_b_aortic_dissection():
    result = run_workflow(CASE_B)
    diagnoses = result.get("candidate_diagnoses", [])
    assert len(diagnoses) > 0
    top = diagnoses[0]["name"]
    assert top == "主动脉夹层", f"Expected 主动脉夹层 as top diagnosis, got {top}"


def test_workflow_case_c_pulmonary_embolism():
    result = run_workflow(CASE_C)
    diagnoses = result.get("candidate_diagnoses", [])
    assert len(diagnoses) > 0
    top = diagnoses[0]["name"]
    assert top == "肺栓塞", f"Expected 肺栓塞 as top diagnosis, got {top}"


def test_workflow_has_case_summary():
    result = run_workflow(CASE_A)
    assert result.get("case_summary", "") != ""


def test_workflow_has_next_steps():
    result = run_workflow(CASE_A)
    assert len(result.get("next_steps", [])) > 0
