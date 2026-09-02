"""Embedding model loader (sentence-transformers)."""
from functools import lru_cache

from config.settings import settings


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed(texts: list[str]):
    return get_model().encode(texts, normalize_embeddings=True)
