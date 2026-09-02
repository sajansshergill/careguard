"""Deterministic classifier used by the mock LLM.

Mirrors the three bundled policies so the demo, tests, and CI run without an
API key. The OpenAI / Ollama path ignores this module and follows the prompt
templates in config/prompts/.
"""
from __future__ import annotations

RED_FLAGS = (
    "malignancy",
    "infection",
    "cauda equina",
    "neurologic deficit",
    "progressive neurologic",
)
LONG_DURATION = (
    "8 weeks",
    "eight weeks",
    "6 weeks",
    "six weeks",
    "two months",
    "8-week",
    "six-week",
)
CONSERVATIVE = ("physical therapy", "nsaid", "conservative", " pt", "pt ", "pt,", "pt.")
ACUTE = ("last week", "acute onset", "three days", "3 days", "few days")
MECHANICAL = ("mechanical", "locking", "catching", "meniscus", "giving way")
OA = ("osteoarthritis", " oa ")
NO_MECHANICAL = (
    "without mechanical",
    "no mechanical",
    "no locking",
    "without locking",
)
HIGH_PRETEST = (
    "high pretest",
    "moderate to severe",
    "severe osa",
    "observed apnea",
)
MISSING_DOCS = (
    "not documented",
    "not clearly documented",
    "criteria not",
    "unclear",
    "incomplete",
    "missing",
    "duration is unclear",
    "duration of symptoms is not",
)


def _find(clauses: list[tuple[str, str]], *needles: str) -> str | None:
    needles_l = [n.lower() for n in needles]
    for cid, text in clauses:
        tl = text.lower()
        if any(n in tl for n in needles_l):
            return cid
    return clauses[0][0] if clauses else None


def _has(blob: str, needles: tuple[str, ...]) -> bool:
    return any(n in blob for n in needles)


def _domain_keys(service: str) -> tuple[str, ...]:
    if any(k in service for k in ("mri", "imaging", "lumbar")):
        return ("mri", "imaging", "lumbar", "pol-imaging")
    if any(k in service for k in ("knee", "arthroscop")):
        return ("knee", "arthroscop", "orthop", "pol-ortho")
    if any(k in service for k in ("sleep", "psg", "polysomn")):
        return ("sleep", "polysomn", "osa", "apnea", "pol-sleep")
    return ("__none__",)


def _result(decision: str, rationale: str, claims: list[dict]) -> dict:
    return {
        "draft_decision": decision,
        "claims": claims,
        "rationale": rationale,
    }


def classify(service: str, notes: str, clauses: list[tuple[str, str]]) -> dict:
    """Return a reasoner-shaped dict: draft_decision, claims, rationale."""
    blob = f"{service}\n{notes}".lower()
    if not clauses:
        return _result(
            "route-to-human",
            "No relevant policy clauses were retrieved; escalating for human review.",
            [],
        )

    service_l = service.lower()
    domain_ok = any(
        any(k in f"{cid} {text}".lower() for k in _domain_keys(service_l))
        for cid, text in clauses
    )
    if not domain_ok:
        cid = clauses[0][0]
        return _result(
            "route-to-human",
            "No on-policy clause covers this service; routing to a human reviewer.",
            [
                {
                    "text": "Retrieved policies do not clearly address the requested service.",
                    "clause_id": cid,
                }
            ],
        )

    if any(k in service_l for k in ("mri", "imaging", "lumbar")):
        return _imaging(blob, clauses)
    if any(k in service_l for k in ("knee", "arthroscop")):
        return _ortho(blob, clauses)
    if any(k in service_l for k in ("sleep", "psg", "polysomn")):
        return _sleep(blob, clauses)

    cid = clauses[0][0]
    return _result(
        "route-to-human",
        "Coverage criteria for this service are not clearly established; routing to a human.",
        [
            {
                "text": "Retrieved policy language does not establish coverage for this service.",
                "clause_id": cid,
            }
        ],
    )


def _imaging(blob: str, clauses: list[tuple[str, str]]) -> dict:
    if _has(blob, RED_FLAGS):
        cid = _find(clauses, "red-flag", "red flag", "malignancy", "cauda equina")
        return _result(
            "approve",
            "Red-flag symptoms support immediate advanced imaging under the policy.",
            [{"text": "Red-flag symptoms are documented and support immediate MRI.", "clause_id": cid}],
        )
    if _has(blob, LONG_DURATION) and _has(blob, CONSERVATIVE):
        cid = _find(clauses, "eligible for coverage", "six weeks despite conservative")
        return _result(
            "approve",
            "Symptom duration and conservative therapy meet the lumbar MRI coverage criteria.",
            [
                {
                    "text": "Low back pain has persisted at least six weeks despite conservative therapy.",
                    "clause_id": cid,
                }
            ],
        )
    if _has(blob, ACUTE) and not _has(blob, RED_FLAGS):
        cid = _find(clauses, "not eligible", "less than six weeks", "uncomplicated acute")
        return _result(
            "deny",
            "Uncomplicated acute low back pain of short duration does not meet MRI criteria.",
            [
                {
                    "text": "MRI is not covered as initial evaluation for uncomplicated acute low back pain.",
                    "clause_id": cid,
                }
            ],
        )
    cid = _find(clauses, "missing documentation", "clinical review")
    return _result(
        "route-to-human",
        "Duration or conservative-therapy documentation is incomplete; routing for clinical review.",
        [
            {
                "text": "Requests missing duration or conservative-treatment documentation should be reviewed.",
                "clause_id": cid,
            }
        ],
    )


def _positive_mechanical(blob: str) -> bool:
    if any(n in blob for n in NO_MECHANICAL):
        return False
    return _has(blob, MECHANICAL)


def _ortho(blob: str, clauses: list[tuple[str, str]]) -> dict:
    if _has(blob, OA) and not _positive_mechanical(blob):
        cid = _find(clauses, "osteoarthritis", "not supported")
        return _result(
            "deny",
            "Arthroscopy solely for osteoarthritis without mechanical symptoms is not covered.",
            [
                {
                    "text": "Coverage is not supported for knee arthroscopy performed solely for osteoarthritis.",
                    "clause_id": cid,
                }
            ],
        )
    if _positive_mechanical(blob) and _has(blob, LONG_DURATION) and _has(blob, CONSERVATIVE):
        cid = _find(clauses, "mechanical symptoms", "eligible for coverage")
        return _result(
            "approve",
            "Mechanical symptoms plus completed conservative care meet arthroscopy criteria.",
            [
                {
                    "text": "Mechanical symptoms and at least six weeks of conservative management are documented.",
                    "clause_id": cid,
                }
            ],
        )
    cid = _find(clauses, "duration is unclear", "clinical review", "documentation must")
    return _result(
        "route-to-human",
        "Conservative-therapy duration or imaging documentation is incomplete; routing for review.",
        [
            {
                "text": "Unclear conservative-therapy duration should be routed for clinical review.",
                "clause_id": cid,
            }
        ],
    )


def _sleep(blob: str, clauses: list[tuple[str, str]]) -> dict:
    if _has(blob, MISSING_DOCS):
        cid = _find(clauses, "do not document", "clinical review")
        return _result(
            "route-to-human",
            "Symptoms, risk factors, or pretest probability are not documented; routing for review.",
            [
                {
                    "text": "Requests that do not document symptoms or pretest probability should be reviewed.",
                    "clause_id": cid,
                }
            ],
        )
    if _has(blob, HIGH_PRETEST):
        cid = _find(clauses, "high pretest", "polysomnography", "eligible for coverage")
        return _result(
            "approve",
            "High pretest probability of moderate-to-severe OSA supports attended in-lab PSG.",
            [
                {
                    "text": "Attended in-lab polysomnography is eligible given high pretest probability.",
                    "clause_id": cid,
                }
            ],
        )
    cid = _find(clauses, "home sleep", "preferred initial")
    return _result(
        "route-to-human",
        "Home sleep testing is preferred as the initial study; routing for review of in-lab necessity.",
        [
            {
                "text": "Home sleep apnea testing is the preferred initial test for uncomplicated adults.",
                "clause_id": cid,
            }
        ],
    )
