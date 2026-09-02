"""Run the labeled set through the graph and score it.

Run:  python -m careguard.eval
"""
from __future__ import annotations

import json

from careguard.eval.graders.accuracy import decision_correct
from careguard.eval.graders.grounding import grounding_score, hallucination_rate
from careguard.eval.graders.llm_judge import judge
from careguard.eval.metrics import summarize
from careguard.eval.report import render
from careguard.graph import run_case
from careguard.utils.timing import timed


def load_eval_set(path: str = "data/labeled/eval_set.json") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(path: str = "data/labeled/eval_set.json") -> dict:
    rows = []
    for case in load_eval_set(path):
        expected = case.pop("expected")
        with timed() as elapsed:
            state = run_case(case)
        judged = judge(state)
        rows.append(
            {
                "case_id": state.get("case_id"),
                "grounding": grounding_score(state),
                "hallucination": hallucination_rate(state),
                "escalated": int(state.get("escalated", False)),
                "correct": int(decision_correct(state, expected)),
                "expected": expected,
                "final_decision": state.get("final_decision"),
                "judge_score": float(judged.get("score", 0.0)),
                "latency_ms": elapsed(),
            }
        )
    summary = summarize(rows)
    render(summary, rows)
    return summary


if __name__ == "__main__":
    main()
