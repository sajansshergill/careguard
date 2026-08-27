"""Retriever agent: pull the policy clauses most relevant to the case."""
from careguard.state import CaseState, Clause
from careguard.retrieval.vector_store import VectorStore
from config.settings import settings

_store = VectorStore.load(settings.index_path)


def retrieve(state: CaseState) -> CaseState:
    query = f"{state['service_requested']} {state['clinical_notes']}"
    hits = _store.query(query, k=settings.top_k)
    state["clauses"] = [
        Clause(clause_id=h["clause_id"], policy_id=h["policy_id"],
               text=h["text"], score=h["score"])
        for h in hits
    ]
    return state