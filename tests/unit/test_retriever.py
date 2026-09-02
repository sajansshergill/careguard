from careguard.agents import retriever as retriever_mod
from careguard.agents.retriever import retrieve
from careguard.retrieval.vector_store import VectorStore


def test_retriever_returns_top_hit(tiny_store):
    retriever_mod.set_store(VectorStore.load(tiny_store))
    try:
        state = retrieve(
            {
                "service_requested": "MRI lumbar spine",
                "clinical_notes": "six weeks of pain",
            }
        )
        assert state["clauses"]
        assert state["clauses"][0].clause_id == "T-1"
        assert state["clauses"][0].score > 0
    finally:
        retriever_mod.set_store(None)
