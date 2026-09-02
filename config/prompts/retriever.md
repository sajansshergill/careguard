# Retriever

Retrieval is handled by vector similarity search, not an LLM call, so this file
documents intent rather than a live prompt.

Goal: surface the policy clauses most relevant to the requested service and the
clinical context. Query is built from `service_requested` + `clinical_notes`.
Return the top-K clauses with their stable clause_id and similarity score.