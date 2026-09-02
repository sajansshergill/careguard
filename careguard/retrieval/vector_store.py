"""Lightweight cosine vector store.

Implements the same add/query/save/load interface you'd get from FAISS or Chroma,
so it's a drop-in swap later. Kept dependency-light so the demo runs anywhere.
"""
from __future__ import annotations

import json
import os

import numpy as np

from careguard.retrieval.embeddings import embed


class VectorStore:
    def __init__(self, vectors=None, meta=None):
        self.vectors = vectors if vectors is not None else np.empty((0, 0))
        self.meta: list[dict] = meta or []

    def add(self, records: list[dict]) -> None:
        """records: [{clause_id, policy_id, text}]"""
        vecs = np.asarray(embed([r["text"] for r in records]))
        self.vectors = vecs if self.vectors.size == 0 else np.vstack([self.vectors, vecs])
        self.meta.extend(records)

    def query(self, text: str, k: int = 4) -> list[dict]:
        if not self.meta:
            return []
        q = np.asarray(embed([text]))[0]
        sims = self.vectors @ q  # normalized => cosine
        idx = np.argsort(-sims)[:k]
        return [{**self.meta[i], "score": float(sims[i])} for i in idx]

    def save(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)
        np.save(os.path.join(path, "vectors.npy"), self.vectors)
        with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f)

    @classmethod
    def load(cls, path: str) -> VectorStore:
        vp = os.path.join(path, "vectors.npy")
        mp = os.path.join(path, "meta.json")
        if not (os.path.exists(vp) and os.path.exists(mp)):
            return cls()
        vectors = np.load(vp)
        with open(mp, encoding="utf-8") as f:
            meta = json.load(f)
        return cls(vectors, meta)
