"""Typed state that flows through the LangGraph state machine."""
from typing import TypedDict, Literal
from pydantic import BaseModel


class Clause(BaseModel):
    clause_id: str          # stable ID we can cite, e.g. "POL-CARDIO-3.2"
    policy_id: str
    text: str
    score: float = 0.0      # retrieval similarity


class Claim(BaseModel):
    text: str               # a single assertion in the rationale
    clause_id: str | None   # the clause it relies on (None = unsupported)
    grounded: bool = False


Decision = Literal["approve", "deny", "route-to-human"]


class CaseState(TypedDict, total=False):
    # inputs
    case_id: str
    service_requested: str
    clinical_notes: str

    # retriever output
    clauses: list[Clause]

    # reasoner output
    draft_decision: Decision
    claims: list[Claim]
    rationale: str

    # guardrail output
    grounding_rate: float
    confidence: float

    # router output
    final_decision: Decision
    escalated: bool