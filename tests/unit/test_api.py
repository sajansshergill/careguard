from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_triage_returns_decision():
    res = client.post(
        "/triage",
        json={
            "case_id": "API-1",
            "service_requested": "MRI lumbar spine",
            "clinical_notes": (
                "8 weeks of low back pain. Physical therapy and NSAIDs documented."
            ),
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["final_decision"] in ("approve", "deny", "route-to-human")
    assert "rationale" in body
    assert "claims" in body
