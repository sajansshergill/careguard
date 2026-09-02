"""FastAPI service.  uvicorn api:app --reload"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from careguard.graph import run_case
from careguard.storage.audit import export_audit, read_audit
from careguard.utils.citations import format_rationale

app = FastAPI(
    title="CareGuard",
    description="Citation-grounded prior-authorization triage. Synthetic data only.",
    version="0.1.0",
)


class CaseIn(BaseModel):
    case_id: str
    service_requested: str
    clinical_notes: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage")
def triage(case: CaseIn):
    state = run_case(case.model_dump())
    return {
        "case_id": case.case_id,
        "final_decision": state["final_decision"],
        "escalated": state["escalated"],
        "confidence": state["confidence"],
        "grounding_rate": state["grounding_rate"],
        "rationale": format_rationale(state),
        "claims": [c.model_dump() for c in state.get("claims", [])],
        "clauses": [c.model_dump() for c in state.get("clauses", [])],
    }


@app.get("/audit")
def audit(limit: int = 50):
    return read_audit(limit=limit)


@app.post("/audit/export")
def audit_export(path: str = "data/audit_export.json"):
    n = export_audit(path)
    return {"path": path, "rows": n}
