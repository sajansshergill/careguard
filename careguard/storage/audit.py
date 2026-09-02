"""Write and read the audit trail for every triaged case."""
from __future__ import annotations

import json
import os
import sqlite3

from careguard.state import CaseState
from careguard.storage.db import get_conn


def write_audit(state: CaseState) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit (case_id, final_decision, escalated, confidence, "
        "grounding_rate, rationale, clauses, claims) VALUES (?,?,?,?,?,?,?,?)",
        (
            state.get("case_id"),
            state.get("final_decision"),
            int(state.get("escalated", False)),
            state.get("confidence"),
            state.get("grounding_rate"),
            state.get("rationale"),
            json.dumps([c.model_dump() for c in state.get("clauses", [])]),
            json.dumps([c.model_dump() for c in state.get("claims", [])]),
        ),
    )
    conn.commit()
    conn.close()


def read_audit(limit: int = 200) -> list[dict]:
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT created_at, case_id, final_decision, escalated, confidence, "
        "grounding_rate, rationale FROM audit ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def export_audit(path: str = "data/audit_export.json") -> int:
    rows = read_audit(limit=10_000)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    return len(rows)
