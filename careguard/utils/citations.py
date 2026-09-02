"""Render a human-readable, cited rationale from graph state."""
from __future__ import annotations

from careguard.state import CaseState


def format_rationale(state: CaseState) -> str:
    lines = [state.get("rationale", "").strip(), "", "Basis:"]
    for c in state.get("claims", []):
        tag = c.clause_id if c.grounded else f"{c.clause_id} (UNVERIFIED)"
        lines.append(f"  • {c.text}  [{tag}]")
    return "\n".join(lines)
