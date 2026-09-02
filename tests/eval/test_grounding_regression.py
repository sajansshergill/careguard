"""CI gate: aggregate grounding on the labeled set must not regress.

If a prompt or model change drops grounding below the floor, this fails the build.
"""
from __future__ import annotations

import json
import os

import pytest

from careguard.eval.graders.grounding import grounding_score
from careguard.graph import run_case

GROUNDING_FLOOR = 0.80
EVAL_PATH = "data/labeled/eval_set.json"


def _eval_set() -> list[dict]:
    if not os.path.exists(EVAL_PATH):
        return []
    try:
        with open(EVAL_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


@pytest.mark.skipif(not _eval_set(), reason="run data/cases/generate_cases.py first")
def test_grounding_above_floor():
    scores = []
    for case in _eval_set():
        case = {k: v for k, v in case.items() if k != "expected"}
        scores.append(grounding_score(run_case(case)))
    mean_grounding = sum(scores) / len(scores)
    assert mean_grounding >= GROUNDING_FLOOR, (
        f"grounding regressed: {mean_grounding:.2f} < {GROUNDING_FLOOR}"
    )
