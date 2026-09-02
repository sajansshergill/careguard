"""Split a policy into citable clauses with stable IDs."""
from __future__ import annotations

import re


def chunk_policy(policy_id: str, text: str) -> list[dict]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    clauses = []
    for i, block in enumerate(blocks, start=1):
        clauses.append(
            {
                "clause_id": f"{policy_id}-{i}",
                "policy_id": policy_id,
                "text": block,
            }
        )
    return clauses
