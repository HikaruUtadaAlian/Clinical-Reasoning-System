from typing import Dict, Any


def format_final_answer(final_answer: Dict[str, Any]) -> str:
    """Format the final answer dict as a human-readable string."""
    if not final_answer:
        return "No result available."

    lines = []
    lines.append(f"【病例摘要】{final_answer.get('case_summary', '')}")
    lines.append("")

    for dx in final_answer.get("candidate_diagnoses", []):
        lines.append(
            f"#{dx.get('rank', '?')} {dx.get('name', '')}  "
            f"(置信度: {dx.get('confidence', 0):.0%})"
        )
        supporting = "、".join(dx.get("supporting_evidence", []))
        lines.append(f"  支持证据: {supporting}")
        tests = "、".join(dx.get("recommended_tests", []))
        lines.append(f"  推荐检查: {tests}")
        mgmt = "、".join(dx.get("initial_management", []))
        lines.append(f"  初始处置: {mgmt}")
        citations = "、".join(dx.get("citations", []))
        lines.append(f"  文献: {citations}")
        lines.append("")

    next_steps = final_answer.get("next_steps", [])
    if next_steps:
        lines.append("【下一步】")
        for step in next_steps:
            lines.append(f"  - {step}")
        lines.append("")

    lines.append(f"⚠️  {final_answer.get('notes', '')}")
    return "\n".join(lines)
