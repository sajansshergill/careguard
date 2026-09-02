from careguard.state import Claim
from careguard.utils.citations import format_rationale


def test_unverified_claims_are_flagged():
    state = {
        "rationale": "Meets criteria.",
        "claims": [
            Claim(text="in scope", clause_id="MOCK-1", grounded=True),
            Claim(text="guessed", clause_id="MOCK-9", grounded=False),
        ],
    }
    out = format_rationale(state)
    assert "MOCK-1" in out
    assert "UNVERIFIED" in out