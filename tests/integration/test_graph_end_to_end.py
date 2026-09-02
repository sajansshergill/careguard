from careguard.graph import run_case


def test_full_pipeline_produces_valid_decision():
    state = run_case({
        "case_id": "E2E-1",
        "service_requested": "MRI lumbar spine",
        "clinical_notes": "8 weeks of pain, PT completed",
    })
    assert state["final_decision"] in ("approve", "deny", "route-to-human")
    assert 0.0 <= state["grounding_rate"] <= 1.0
    assert 0.0 <= state["confidence"] <= 1.0