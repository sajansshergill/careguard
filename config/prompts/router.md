# Router

Routing is deterministic logic, not an LLM call.

Rules:
- Auto-decide (approve/deny) only when confidence >= threshold AND every claim
  is grounded AND the draft decision is approve or deny.
- Otherwise route-to-human.

The bar is deliberately conservative: when in doubt, escalate.