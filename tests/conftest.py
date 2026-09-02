"""Shared fixtures. Forces mock LLM so the suite runs with no API key."""
from __future__ import annotations

import os

os.environ.setdefault("LLM_PROVIDER", "mock")

import pytest  # noqa: E402

from careguard.ingest.build_index import main as build_index  # noqa: E402
from careguard.retrieval.vector_store import VectorStore  # noqa: E402
from careguard.state import CaseState, Claim, Clause  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _ensure_index():
    """Build the policy index once so graph tests retrieve real clauses."""
    from pathlib import Path

    marker = Path("data/index/vectors.npy")
    if not marker.exists():
        build_index("data/policies/")


@pytest.fixture
def sample_clauses():
    return [
        Clause(clause_id="MOCK-1", policy_id="MOCK", text="Service is in scope.", score=0.9),
        Clause(
            clause_id="MOCK-2",
            policy_id="MOCK",
            text="Conservative therapy documented.",
            score=0.8,
        ),
    ]


@pytest.fixture
def grounded_state(sample_clauses) -> CaseState:
    return {
        "case_id": "FIX-1",
        "clauses": sample_clauses,
        "claims": [
            Claim(text="in scope", clause_id="MOCK-1", grounded=True),
            Claim(text="therapy documented", clause_id="MOCK-2", grounded=True),
        ],
        "draft_decision": "approve",
    }


@pytest.fixture
def tiny_store(tmp_path):
    store = VectorStore()
    store.add(
        [
            {"clause_id": "T-1", "policy_id": "T", "text": "MRI lumbar spine after six weeks."},
            {
                "clause_id": "T-2",
                "policy_id": "T",
                "text": "Knee arthroscopy after conservative care.",
            },
        ]
    )
    dest = str(tmp_path / "index")
    store.save(dest)
    return dest
