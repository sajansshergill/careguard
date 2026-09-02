"""Typed state that flows through the LangGraph state machine."""
from __future__ import annotations

from typing import Literal, TypedDict

from pydantic import BaseModel


class Clause(BaseModel):
    clause_id: str
    policy_id: str
    text: str
    score: float = 0.0


class Claim(BaseModel):
    text: str
    clause_id: str | None
    grounded: bool = False


Decision = Literal["approve", "deny", "route-to-human"]


class CaseState(TypedDict, total=False):
    case_id: str
    service_requested: str
    clinical_notes: str
    clauses: list[Clause]
    draft_decision: Decision
    claims: list[Claim]
    rationale: str
    grounding_rate: float
    confidence: float
    final_decision: Decision
    escalated: bool
