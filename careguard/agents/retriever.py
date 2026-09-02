"""Retriever agent: pull the policy clauses most relevant to the case."""
from __future__ import annotations

from careguard.retrieval.vector_store import VectorStore
from careguard.state import CaseState, Clause
from config.settings import settings

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore.load(settings.index_path)
    return _store


def set_store(store: VectorStore | None) -> None:
    """Inject or invalidate the cached store (tests + ingest)."""
    global _store
    _store = store


def retrieve(state: CaseState) -> CaseState:
    query = f"{state['service_requested']} {state['clinical_notes']}"
    hits = get_store().query(query, k=settings.top_k)
    state["clauses"] = [
        Clause(
            clause_id=h["clause_id"],
            policy_id=h["policy_id"],
            text=h["text"],
            score=h["score"],
        )
        for h in hits
    ]
    return state
