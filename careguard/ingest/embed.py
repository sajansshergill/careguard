"""Embed policy clauses into vectors.

The vector store calls sentence-transformers during `add()`. This module is the
ingest-side wrapper so the pipeline can embed without importing the store.
"""
from __future__ import annotations

from careguard.retrieval.embeddings import embed


def embed_clauses(clauses: list[dict]):
    """Return a numpy array of embeddings aligned with `clauses`."""
    return embed([c["text"] for c in clauses])
