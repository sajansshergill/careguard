"""SQL schema for the audit trail (decision + retrieved context per case)."""

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit (
    case_id        TEXT,
    final_decision TEXT,
    escalated      INTEGER,
    confidence     REAL,
    grounding_rate REAL,
    rationale      TEXT,
    clauses        TEXT,
    claims         TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
