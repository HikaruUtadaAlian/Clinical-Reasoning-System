from typing import Dict, Any

from langgraph.graph import StateGraph, END

from src.state import AppState
from src.agents.case_parser import run_case_parser
from src.agents.doc_retriever import run_doc_retriever
from src.agents.graph_retriever import run_graph_retriever
from src.agents.reasoner import run_reasoner


def build_workflow():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AppState)

    workflow.add_node("case_parser", run_case_parser)
    workflow.add_node("doc_retriever", run_doc_retriever)
    workflow.add_node("graph_retriever", run_graph_retriever)
    workflow.add_node("reasoner", run_reasoner)

    workflow.set_entry_point("case_parser")
    workflow.add_edge("case_parser", "doc_retriever")
    workflow.add_edge("doc_retriever", "graph_retriever")
    workflow.add_edge("graph_retriever", "reasoner")
    workflow.add_edge("reasoner", END)

    return workflow.compile()


def run_workflow(case_text: str) -> Dict[str, Any]:
    """Run the full workflow on a case text and return the final_answer."""
    app = build_workflow()
    initial_state: AppState = {
        "case_text": case_text,
        "logs": [],
    }
    result = app.invoke(initial_state)
    return result.get("final_answer", {})
