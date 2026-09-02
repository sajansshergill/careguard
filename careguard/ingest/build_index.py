"""Ingest pipeline. Parse/clean/chunk -> vector store.

Run:  python -m careguard.ingest --source data/policies/

Uses PySpark when available, otherwise a plain-Python fallback.
"""
from __future__ import annotations

import argparse

from careguard.agents.retriever import set_store
from careguard.ingest.chunk import chunk_policy
from careguard.ingest.clean import clean_text
from careguard.ingest.parse import load_policies
from careguard.retrieval.vector_store import VectorStore
from config.settings import settings


def _chunks_spark(docs: list[dict]) -> list[dict]:
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("careguard-ingest").getOrCreate()
    rdd = spark.sparkContext.parallelize(docs)
    clauses = (
        rdd.map(lambda d: {**d, "text": clean_text(d["text"])})
        .flatMap(lambda d: chunk_policy(d["policy_id"], d["text"]))
        .collect()
    )
    spark.stop()
    return clauses


def _chunks_python(docs: list[dict]) -> list[dict]:
    out = []
    for doc in docs:
        out.extend(chunk_policy(doc["policy_id"], clean_text(doc["text"])))
    return out


def main(source: str = "data/policies/") -> None:
    docs = load_policies(source)
    try:
        clauses = _chunks_spark(docs)
        print(f"[ingest] PySpark path: {len(clauses)} clauses")
    except Exception as exc:  # noqa: BLE001
        clauses = _chunks_python(docs)
        print(f"[ingest] Python fallback ({exc}): {len(clauses)} clauses")

    store = VectorStore()
    store.add(clauses)
    store.save(settings.index_path)
    set_store(None)  # next retrieve() reloads the new index
    print(f"[ingest] index written to {settings.index_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="data/policies/")
    main(ap.parse_args().source)
