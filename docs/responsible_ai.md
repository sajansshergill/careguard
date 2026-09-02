# Responsible-AI design

The guardrails are the point of the project, not decoration.

## Citation grounding
Every claim in a rationale must reference the clause it relied on. The Guardrail
agent validates those citations against the actually-retrieved text; a claim
whose clause isn't present is marked ungrounded and rendered with an
`(UNVERIFIED)` tag.

## Grounding gates confidence
`aggregate_confidence` takes the *minimum* of the model's confidence and the
grounding rate. One unverifiable claim caps how confident the system may be —
so the system cannot be both confidently wrong and ungrounded.

## Abstention over guessing
The Router auto-decides only when confidence clears the threshold AND all claims
are grounded AND the draft is approve or deny. Everything else routes to a
human. The bar is deliberately conservative for a healthcare context.

## Auditability
Every case writes inputs, retrieved context, reasoning, claims, decision, and
scores to an audit table (`storage/audit.py`) for later review. The API exposes
`GET /audit`; `export_audit()` dumps a JSON file.

## Measured, not assumed
Grounding rate, hallucination rate, escalation rate, judge score, and latency
are tracked by the eval harness and gated in CI, so behavior can't silently
regress. The metrics dashboard reads the latest report plus the live audit log.

## Data boundary
Synthetic and public data only. No PHI enters the system at any point. The
bundled cases in `data/cases/` and `data/labeled/` are fabricated.
