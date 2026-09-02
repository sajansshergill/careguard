"""Compare final decision against a labeled expected outcome."""
from __future__ import annotations

from careguard.state import CaseState


def decision_correct(state: CaseState, expected: str) -> bool:
    return state.get("final_decision") == expected
