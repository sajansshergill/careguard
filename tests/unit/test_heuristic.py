from careguard.agents.heuristic import classify


def _clauses(*pairs: tuple[str, str]):
    return list(pairs)


IMAGING = _clauses(
    (
        "POL-IMAGING-2",
        "MRI of the lumbar spine is eligible for coverage when six weeks of conservative therapy.",
    ),
    (
        "POL-IMAGING-3",
        "MRI is not eligible as an initial evaluation for uncomplicated acute low back pain of less than six weeks.",
    ),
    (
        "POL-IMAGING-4",
        "Red-flag symptoms that support immediate advanced imaging include cauda equina.",
    ),
    (
        "POL-IMAGING-5",
        "Requests missing documentation should be routed for clinical review.",
    ),
)


def test_mri_long_duration_approves():
    out = classify(
        "MRI lumbar spine",
        "8 weeks of pain; physical therapy and NSAIDs documented.",
        IMAGING,
    )
    assert out["draft_decision"] == "approve"


def test_mri_acute_denies():
    out = classify(
        "MRI lumbar spine",
        "Acute onset last week of uncomplicated low back pain.",
        IMAGING,
    )
    assert out["draft_decision"] == "deny"


def test_empty_clauses_escalate():
    out = classify("MRI lumbar spine", "8 weeks of PT", [])
    assert out["draft_decision"] == "route-to-human"
    assert out["claims"] == []
