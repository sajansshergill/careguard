from careguard.agents.guardrail import guard
from careguard.state import Claim


def test_guardrail_marks_real_citations_grounded(sample_clauses):
    state = {
        "clauses": sample_clauses,
        "claims": [
            Claim(text="in scope", clause_id="MOCK-1"),
            Claim(text="guessed", clause_id="NOPE"),
        ],
    }
    out = guard(state)
    assert out["claims"][0].grounded is True
    assert out["claims"][1].grounded is False
    assert out["grounding_rate"] == 0.5
    assert out["confidence"] <= out["grounding_rate"] + 1e-9


def test_all_grounded_when_ids_exist(sample_clauses):
    state = {
        "clauses": sample_clauses,
        "claims": [
            Claim(text="in scope", clause_id="MOCK-1"),
            Claim(text="therapy documented", clause_id="MOCK-2"),
        ],
    }
    out = guard(state)
    assert out["grounding_rate"] == 1.0
    assert out["confidence"] >= 0.70
