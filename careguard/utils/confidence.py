"""Confidence aggregation: penalize ungrounded reasoning hard."""
from __future__ import annotations


def aggregate_confidence(grounding_rate: float, llm_confidence: float) -> float:
    return round(min(grounding_rate, llm_confidence), 4)
