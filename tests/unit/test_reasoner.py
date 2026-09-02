from careguard.agents.reasoner import reason
from careguard.state import Clause


def test_reasoner_cites_only_retrieved_ids(sample_clauses):
    out = reason(
        {
            "service_requested": "MRI lumbar spine",
            "clinical_notes": "8 weeks of PT and NSAIDs",
            "clauses": sample_clauses,
        }
    )
    retrieved = {c.clause_id for c in sample_clauses}
    assert out["claims"]
    for claim in out["claims"]:
        assert claim.clause_id in retrieved
    assert out["draft_decision"] in ("approve", "deny", "route-to-human")


def test_reasoner_approves_documented_mri():
    clauses = [
        Clause(
            clause_id="POL-IMAGING-2",
            policy_id="POL-IMAGING",
            text=(
                "MRI of the lumbar spine is eligible for coverage when the member "
                "has documented low back pain persisting for at least six weeks "
                "despite conservative therapy, including physical therapy or NSAIDs."
            ),
            score=0.9,
        ),
        Clause(
            clause_id="POL-IMAGING-3",
            policy_id="POL-IMAGING",
            text="MRI is not eligible as an initial evaluation for uncomplicated acute pain.",
            score=0.4,
        ),
    ]
    out = reason(
        {
            "service_requested": "MRI lumbar spine",
            "clinical_notes": (
                "8 weeks of symptoms; physical therapy and NSAIDs documented."
            ),
            "clauses": clauses,
        }
    )
    assert out["draft_decision"] == "approve"
    assert all(c.clause_id.startswith("POL-IMAGING") for c in out["claims"])
