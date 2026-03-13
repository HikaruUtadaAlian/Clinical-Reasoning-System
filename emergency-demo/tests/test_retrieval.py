import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.text_search import load_chunks, search_chunks
from src.retrieval.graph_search import load_graph, search_graph

DATA_DIR = Path(__file__).parent.parent / "data"


def test_text_search_returns_results():
    chunks = load_chunks(str(DATA_DIR / "chunks.jsonl"))
    hits = search_chunks(["胸痛", "ST段抬高"], chunks, top_k=5)
    assert len(hits) > 0
    assert all("_score" in h for h in hits)


def test_text_search_stemi_terms():
    chunks = load_chunks(str(DATA_DIR / "chunks.jsonl"))
    hits = search_chunks(["ST段抬高", "出汗"], chunks, top_k=5)
    diseases = [h["disease"] for h in hits]
    assert "STEMI" in diseases


def test_graph_search_returns_candidates():
    graph = load_graph(str(DATA_DIR / "graph.json"))
    graph_hits, candidates = search_graph(["胸痛", "ST段抬高", "出汗"], graph, top_k=3)
    assert len(candidates) > 0


def test_graph_search_stemi_candidate():
    graph = load_graph(str(DATA_DIR / "graph.json"))
    _, candidates = search_graph(["ST段抬高", "出汗"], graph, top_k=3)
    disease_names = [c["disease"] for c in candidates]
    assert "STEMI" in disease_names


def test_graph_search_pe_candidate():
    graph = load_graph(str(DATA_DIR / "graph.json"))
    _, candidates = search_graph(["呼吸困难", "心动过速", "D-dimer升高"], graph, top_k=3)
    disease_names = [c["disease"] for c in candidates]
    assert "肺栓塞" in disease_names
