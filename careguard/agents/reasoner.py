"""Reasoner agent: evaluate the case against retrieved criteria."""
from __future__ import annotations

from careguard.agents.base import llm
from careguard.state import CaseState, Claim
from config.prompts import load_prompt


def reason(state: CaseState) -> CaseState:
    clause_block = "\n".join(f"[{c.clause_id}] {c.text}" for c in state["clauses"])
    user = (
        f"SERVICE REQUESTED: {state['service_requested']}\n"
        f"CLINICAL NOTES: {state['clinical_notes']}\n\n"
        f"RETRIEVED CLAUSES:\n{clause_block}"
    )
    out = llm.complete_json(load_prompt("reasoner"), user)
    state["draft_decision"] = out.get("draft_decision", "route-to-human")
    state["claims"] = [
        Claim(text=c["text"], clause_id=c.get("clause_id")) for c in out.get("claims", [])
    ]
    state["rationale"] = out.get("rationale", "")
    return state
