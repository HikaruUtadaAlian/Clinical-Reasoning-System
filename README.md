# Clinical-Reasoning-System

A rule-based emergency clinical reasoning system for acute chest pain triage.

## Quick Start — Emergency Demo

```bash
# 1. Install dependencies
cd emergency-demo
pip install -r requirements.txt

# 2. Run the Streamlit web app
streamlit run app/streamlit_app.py
```

Open the URL shown in the terminal (default: http://localhost:8501).

## Running Tests

```bash
cd emergency-demo
python -m pytest tests/ -v
```

## Project Structure

```
emergency-demo/
├── app/                  # Streamlit UI (streamlit_app.py, components.py)
├── data/                 # Local knowledge base (chunks.jsonl, graph.json, demo_cases.json)
├── src/
│   ├── state.py          # AppState TypedDict
│   ├── graph_workflow.py # LangGraph pipeline
│   ├── agents/           # case_parser, doc_retriever, graph_retriever, reasoner
│   ├── retrieval/        # text_search, graph_search
│   ├── utils/            # io, logger, formatting
│   └── prompts/          # Prompt templates for future LLM integration
└── tests/                # pytest test suite
```

## Covered Diseases

| Disease | Chinese |
|---------|---------|
| STEMI | ST段抬高型心肌梗死 |
| Aortic Dissection | 主动脉夹层 |
| Pulmonary Embolism | 肺栓塞 |

> ⚠️ For teaching and demonstration purposes only. Not for clinical use.
