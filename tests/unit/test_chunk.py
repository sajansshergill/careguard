from careguard.ingest.chunk import chunk_policy


def test_chunk_assigns_stable_ids():
    text = "First clause.\n\nSecond clause.\n\nThird clause."
    clauses = chunk_policy("POL-X", text)
    assert [c["clause_id"] for c in clauses] == ["POL-X-1", "POL-X-2", "POL-X-3"]
    assert clauses[0]["policy_id"] == "POL-X"