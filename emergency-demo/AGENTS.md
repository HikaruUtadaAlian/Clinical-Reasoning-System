# AGENTS.md — Emergency Clinical Reasoning System

## Project Goal

Build a rule-based emergency clinical reasoning system that performs differential
diagnosis for acute chest pain cases, covering three diseases:

1. **STEMI** (ST段抬高型心肌梗死)
2. **主动脉夹层** (Aortic Dissection)
3. **肺栓塞** (Pulmonary Embolism)

The system parses a free-text clinical case, retrieves relevant document chunks and
knowledge-graph evidence, and synthesizes a ranked differential diagnosis — all
without any LLM API calls (pure rule-based MVP).

## Scope

- **In scope**: chest pain triage, 3 diseases only (STEMI, 主动脉夹层, 肺栓塞)
- **Out of scope**: other diagnoses, LLM integration, real-time EHR data, production deployment

**Do not expand scope.** Adding new diseases or data sources requires explicit approval and
corresponding updates to `data/graph.json`, `data/chunks.jsonl`, and agent logic.

## Data

All data lives in `emergency-demo/data/`:
- `chunks.jsonl` — document chunks (local, no external calls)
- `graph.json` — knowledge graph (local, no external calls)
- `demo_cases.json` — demo cases A, B, C

Do **not** add external API calls for data retrieval.

## Workflow Stability

- Prioritize workflow stability over feature richness.
- The LangGraph pipeline (START → case_parser → doc_retriever → graph_retriever → reasoner → END)
  must not be re-ordered without thorough testing.
- Each agent function must return the full state dict (spread operator `{**state, ...}`).

## Self-Check After Changes

After any code change, run:

```bash
cd emergency-demo && python -m pytest tests/ -v
```

All tests must pass before committing.

## Running the App

```bash
cd emergency-demo
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## File Overview

```
emergency-demo/
├── app/                  # Streamlit UI
│   ├── streamlit_app.py
│   └── components.py
├── data/                 # Local knowledge data
│   ├── chunks.jsonl
│   ├── graph.json
│   └── demo_cases.json
├── src/
│   ├── state.py          # AppState TypedDict
│   ├── graph_workflow.py # LangGraph pipeline
│   ├── agents/           # Pipeline nodes
│   ├── retrieval/        # Search utilities
│   ├── utils/            # IO, logging, formatting
│   └── prompts/          # Future LLM prompt templates
└── tests/                # pytest test suite
```
