"""Guardrail/Critic agent: verify each claim is grounded; score confidence."""
from careguard.agents.base import llm
from careguard.state import CaseState
from careguard.utils.confidence import aggregate_confidence

SYSTEM = """You are the Guardrail critic. For each claim, decide whether the cited
clause actually EXISTS in the provided clauses AND supports the claim. Return
grounded_clause_ids (the subset of cited ids that are valid) and a confidence
score in [0,1] reflecting how well the decision is supported."""


def guard(state: CaseState) -> CaseState:
    valid_ids = {c.clause_id for c in state["clauses"]}
    clause_block = "\n".join(f"[{c.clause_id}] {c.text}" for c in state["clauses"])
    claim_block = "\n".join(
        f"- {c.text} (cites {c.clause_id})" for c in state["claims"]
    )
    out = llm.complete_json(
        SYSTEM,
        f"CLAUSES:\n{clause_block}\n\nCLAIMS:\n{claim_block}",
    )
    grounded = set(out.get("grounded_clause_ids", [])) & valid_ids

    # mark grounding on each claim and compute the rate deterministically
    for c in state["claims"]:
        c.grounded = c.clause_id in grounded
    total = len(state["claims"]) or 1
    state["grounding_rate"] = sum(c.grounded for c in state["claims"]) / total

    llm_conf = float(out.get("confidence", 0.0))
    state["confidence"] = aggregate_confidence(state["grounding_rate"], llm_conf)
    return state