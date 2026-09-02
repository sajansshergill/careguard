"""Guardrail/Critic agent: verify each claim is grounded; score confidence."""
from __future__ import annotations

from careguard.agents.base import llm
from careguard.state import CaseState
from careguard.utils.confidence import aggregate_confidence
from config.prompts import load_prompt


def guard(state: CaseState) -> CaseState:
    valid_ids = {c.clause_id for c in state["clauses"]}
    clause_block = "\n".join(f"[{c.clause_id}] {c.text}" for c in state["clauses"])
    claim_block = "\n".join(f"- {c.text} (cites {c.clause_id})" for c in state["claims"])
    out = llm.complete_json(
        load_prompt("guardrail"),
        f"CLAUSES:\n{clause_block}\n\nCLAIMS:\n{claim_block}",
    )
    grounded = set(out.get("grounded_clause_ids", [])) & valid_ids

    for claim in state["claims"]:
        claim.grounded = claim.clause_id in grounded
    total = len(state["claims"]) or 1
    state["grounding_rate"] = sum(c.grounded for c in state["claims"]) / total

    llm_conf = float(out.get("confidence", 0.0))
    state["confidence"] = aggregate_confidence(state["grounding_rate"], llm_conf)
    return state
