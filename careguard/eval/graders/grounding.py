"""Rule-based grader: does every cited clause exist and get marked grounded?"""
from __future__ import annotations

from careguard.state import CaseState


def grounding_score(state: CaseState) -> float:
    claims = state.get("claims", [])
    if not claims:
        return 0.0
    return sum(c.grounded for c in claims) / len(claims)


def hallucination_rate(state: CaseState) -> float:
    return 1.0 - grounding_score(state)
