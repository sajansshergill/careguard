"""LLM-as-judge grader.

A second-opinion scorer that asks a model whether the rationale is well-supported
by the cited clauses. Complements the deterministic grounding grader — the two
disagreeing is itself a useful signal. Runs against the mock provider too.
"""
from __future__ import annotations

from careguard.agents.base import llm
from careguard.state import CaseState

SYSTEM = """You are an impartial judge of prior-authorization rationales.
Given the retrieved clauses and the system's rationale + cited claims, rate how
well the decision is supported by the cited clauses. Return JSON:
{ "supported": true|false, "score": 0..1, "reason": "..." }"""


def judge(state: CaseState) -> dict:
    clause_block = "\n".join(f"[{c.clause_id}] {c.text}" for c in state.get("clauses", []))
    claim_block = "\n".join(
        f"- {c.text} (cites {c.clause_id})" for c in state.get("claims", [])
    )
    user = (
        f"CLAUSES:\n{clause_block}\n\n"
        f"RATIONALE:\n{state.get('rationale', '')}\n\n"
        f"CLAIMS:\n{claim_block}"
    )
    try:
        out = llm.complete_json(SYSTEM, user)
    except Exception:  # noqa: BLE001 — judge must never crash the harness
        return {"supported": False, "score": 0.0, "reason": "judge_error"}
    return {
        "supported": bool(out.get("supported", False)),
        "score": float(out.get("score", 0.0)),
        "reason": out.get("reason", ""),
    }
