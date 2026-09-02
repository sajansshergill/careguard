"""Aggregate per-case results into headline metrics."""
from __future__ import annotations

from statistics import mean


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {
            "n": 0,
            "policy_grounding_rate": 0.0,
            "hallucination_rate": 0.0,
            "escalation_rate": 0.0,
            "decision_accuracy": 0.0,
            "judge_score": 0.0,
            "p95_latency_ms": 0.0,
        }
    labeled = [r for r in rows if r["expected"] in ("approve", "deny")]
    latencies = sorted(r["latency_ms"] for r in rows)
    p95_idx = max(0, int(0.95 * len(latencies)) - 1)
    return {
        "n": len(rows),
        "policy_grounding_rate": round(mean(r["grounding"] for r in rows), 3),
        "hallucination_rate": round(mean(r["hallucination"] for r in rows), 3),
        "escalation_rate": round(mean(r["escalated"] for r in rows), 3),
        "decision_accuracy": round(mean(r["correct"] for r in labeled), 3) if labeled else 0.0,
        "judge_score": round(mean(r.get("judge_score", 0.0) for r in rows), 3),
        "p95_latency_ms": round(latencies[p95_idx], 1),
    }
