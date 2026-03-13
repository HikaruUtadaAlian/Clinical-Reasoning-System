import streamlit as st
import json
from pathlib import Path
import sys

# Ensure src is on the path when running from the emergency-demo directory
_DEMO_ROOT = Path(__file__).parent.parent
if str(_DEMO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_DEMO_ROOT))

from src.graph_workflow import run_workflow
from src.utils.io import load_json
from app.components import render_diagnosis_card, render_debug_section

DATA_DIR = _DEMO_ROOT / "data"


def main():
    st.set_page_config(
        page_title="急诊病例智能推理系统",
        page_icon="🏥",
        layout="wide",
    )
    st.title("🏥 急诊病例智能推理系统")
    st.caption("仅供教学与演示使用，不构成临床建议。")

    # Load demo cases for sidebar
    demo_cases = load_json(str(DATA_DIR / "demo_cases.json"))
    case_labels = ["(自定义输入)"] + [c["label"] for c in demo_cases]

    with st.sidebar:
        st.header("演示病例")
        selected_label = st.selectbox("选择演示病例", case_labels)
        st.markdown("---")
        st.markdown("**系统说明**")
        st.markdown(
            "本系统基于规则引擎对急诊胸痛进行鉴别诊断，\n"
            "覆盖：STEMI、主动脉夹层、肺栓塞。"
        )

    # Determine default text
    default_text = ""
    if selected_label != "(自定义输入)":
        for c in demo_cases:
            if c["label"] == selected_label:
                default_text = c["text"]
                break

    case_input = st.text_area(
        "请输入病例描述",
        value=default_text,
        height=150,
        placeholder="例如：65岁男性，胸痛2小时，出汗，血压90/60，ECG示ST段抬高。",
    )

    if st.button("🔍 开始分析", type="primary"):
        if not case_input.strip():
            st.warning("请先输入病例描述。")
            return

        with st.spinner("正在分析中，请稍候…"):
            try:
                # Run full workflow; also capture state for debug
                from src.graph_workflow import build_workflow
                from src.state import AppState

                app = build_workflow()
                initial_state: AppState = {"case_text": case_input, "logs": []}
                state = app.invoke(initial_state)
                final_answer = state.get("final_answer", {})
            except Exception as exc:
                st.error(f"分析失败：{exc}")
                return

        if not final_answer:
            st.error("未能生成分析结果，请检查输入。")
            return

        # ── Results ─────────────────────────────────────────────
        st.subheader("📋 病例摘要")
        st.info(final_answer.get("case_summary", ""))

        st.subheader("🔬 鉴别诊断")
        for dx in final_answer.get("candidate_diagnoses", []):
            render_diagnosis_card(dx)

        next_steps = final_answer.get("next_steps", [])
        if next_steps:
            st.subheader("⚡ 下一步处置")
            for step in next_steps:
                st.markdown(f"- {step}")

        st.caption(f"⚠️ {final_answer.get('notes', '')}")

        render_debug_section(state)


if __name__ == "__main__":
    main()
