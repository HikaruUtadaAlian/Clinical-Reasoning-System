import streamlit as st
from typing import Dict, Any


def render_diagnosis_card(diagnosis: Dict[str, Any]) -> None:
    """Render a single diagnosis as a Streamlit expander card."""
    name = diagnosis.get("name", "未知")
    rank = diagnosis.get("rank", "?")
    confidence = diagnosis.get("confidence", 0.0)
    pct = int(confidence * 100)

    label = f"#{rank}  {name}  —  置信度 {pct}%"
    with st.expander(label, expanded=(rank == 1)):
        col1, col2 = st.columns(2)

        with col1:
            st.progress(confidence)
            supporting = diagnosis.get("supporting_evidence", [])
            if supporting:
                st.markdown("**支持证据**")
                for ev in supporting:
                    st.markdown(f"  ✅ {ev}")
            against = diagnosis.get("against_evidence", [])
            if against:
                st.markdown("**不支持证据**")
                for ev in against:
                    st.markdown(f"  ❌ {ev}")

        with col2:
            tests = diagnosis.get("recommended_tests", [])
            if tests:
                st.markdown("**推荐检查**")
                for t in tests:
                    st.markdown(f"  🔬 {t}")
            mgmt = diagnosis.get("initial_management", [])
            if mgmt:
                st.markdown("**初始处置**")
                for m in mgmt:
                    st.markdown(f"  💊 {m}")

        citations = diagnosis.get("citations", [])
        if citations:
            st.markdown("**文献来源**")
            st.caption("  " + "、".join(citations))


def render_debug_section(state: Dict[str, Any]) -> None:
    """Render a collapsible debug section showing raw retrieval results."""
    with st.expander("🛠 调试信息 (Debug)", expanded=False):
        doc_hits = state.get("doc_hits", [])
        graph_hits = state.get("graph_hits", [])
        logs = state.get("logs", [])

        st.markdown(f"**文档命中 ({len(doc_hits)} 条)**")
        for hit in doc_hits:
            st.markdown(
                f"- [{hit.get('disease','')}] {hit.get('text','')[:60]}…  "
                f"`score={hit.get('_score',0)}`"
            )

        st.markdown(f"**图谱命中 ({len(graph_hits)} 个节点)**")
        for node in graph_hits:
            st.markdown(f"- {node.get('label','')} ({node.get('type','')})")

        if logs:
            st.markdown("**日志**")
            st.code("\n".join(logs))
