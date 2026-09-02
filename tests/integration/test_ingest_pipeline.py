from careguard.retrieval.vector_store import VectorStore


def test_index_roundtrip_and_query(tiny_store):
    store = VectorStore.load(tiny_store)
    hits = store.query("MRI of the lower back", k=1)
    assert hits
    assert hits[0]["clause_id"] == "T-1"      # semantically closest clause
    assert "score" in hits[0]