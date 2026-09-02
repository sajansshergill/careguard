"""Router: auto-resolve when confident, otherwise escalate to a human."""
from __future__ import annotations

from careguard.state import CaseState
from config.settings import settings


def route(state: CaseState) -> CaseState:
    confident = state["confidence"] >= settings.confidence_threshold
    grounded = state["grounding_rate"] >= 0.99  # every claim must be grounded

    if confident and grounded and state["draft_decision"] in ("approve", "deny"):
        state["final_decision"] = state["draft_decision"]
        state["escalated"] = False
    else:
        state["final_decision"] = "route-to-human"
        state["escalated"] = True
    return state
