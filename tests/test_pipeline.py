"""Smoke + guardrail regression tests (run with LLM_PROVIDER=mock)."""
from careguard.graph import run_case


def test_end_to_end_runs():
    state = run_case(
        {
            "case_id": "T-1",
            "service_requested": "MRI lumbar spine",
            "clinical_notes": "conservative therapy documented",
        }
    )
    assert state["final_decision"] in ("approve", "deny", "route-to-human")
    assert 0.0 <= state["confidence"] <= 1.0


def test_incomplete_docs_escalate():
    state = run_case(
        {
            "case_id": "T-2",
            "service_requested": "sleep study",
            "clinical_notes": "criteria not clearly documented",
        }
    )
    assert state["escalated"] is True
    assert state["final_decision"] == "route-to-human"


def test_documented_mri_auto_approves():
    state = run_case(
        {
            "case_id": "T-MRI",
            "service_requested": "MRI lumbar spine",
            "clinical_notes": (
                "Patient reports 8 weeks of low back pain. Physical therapy and a "
                "trial of NSAIDs are documented. No red-flag symptoms."
            ),
        }
    )
    assert state["final_decision"] == "approve"
    assert state["escalated"] is False
    assert state["grounding_rate"] == 1.0


def test_grounding_never_exceeds_confidence():
    state = run_case(
        {
            "case_id": "T-3",
            "service_requested": "knee arthroscopy",
            "clinical_notes": "failed 6 weeks PT",
        }
    )
    assert state["confidence"] <= state["grounding_rate"] + 1e-9
