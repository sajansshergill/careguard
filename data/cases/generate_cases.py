"""Generate a small synthetic PA case set. NO PHI — fully fabricated.

Writes both the labeled eval set and a demo-facing copy without labels.
"""
from __future__ import annotations

import json
import os

# Curated against data/policies/*.txt so expected labels match the mock heuristic
# and (for a capable model) the real policy text.
CASES = [
    {
        "case_id": "CASE-001",
        "service_requested": "MRI lumbar spine",
        "clinical_notes": (
            "Patient reports 8 weeks of low back pain. Physical therapy and a "
            "trial of NSAIDs are documented. No red-flag symptoms."
        ),
        "expected": "approve",
    },
    {
        "case_id": "CASE-002",
        "service_requested": "MRI lumbar spine",
        "clinical_notes": (
            "Acute onset last week of uncomplicated low back pain. No prior "
            "imaging. No red-flag symptoms."
        ),
        "expected": "deny",
    },
    {
        "case_id": "CASE-003",
        "service_requested": "MRI lumbar spine",
        "clinical_notes": (
            "Three days of severe back pain with suspected cauda equina syndrome "
            "and progressive neurologic deficit."
        ),
        "expected": "approve",
    },
    {
        "case_id": "CASE-004",
        "service_requested": "MRI lumbar spine",
        "clinical_notes": (
            "Low back pain reported. Duration of symptoms is not documented and "
            "prior conservative treatment is missing from the record."
        ),
        "expected": "route-to-human",
    },
    {
        "case_id": "CASE-005",
        "service_requested": "knee arthroscopy",
        "clinical_notes": (
            "Mechanical symptoms with locking. Completed 6 weeks of physical therapy. "
            "Imaging shows meniscus tear."
        ),
        "expected": "approve",
    },
    {
        "case_id": "CASE-006",
        "service_requested": "knee arthroscopy",
        "clinical_notes": (
            "Requested solely for osteoarthritis without mechanical symptoms. "
            "No locking or catching."
        ),
        "expected": "deny",
    },
    {
        "case_id": "CASE-007",
        "service_requested": "knee arthroscopy",
        "clinical_notes": (
            "Mechanical symptoms present. Conservative therapy attempted but "
            "duration is unclear."
        ),
        "expected": "route-to-human",
    },
    {
        "case_id": "CASE-008",
        "service_requested": "in-lab sleep study",
        "clinical_notes": (
            "Documented high pretest probability of moderate to severe obstructive "
            "sleep apnea with observed apnea."
        ),
        "expected": "approve",
    },
    {
        "case_id": "CASE-009",
        "service_requested": "sleep study",
        "clinical_notes": (
            "Symptoms, risk factors, and pretest probability are not documented."
        ),
        "expected": "route-to-human",
    },
    {
        "case_id": "CASE-010",
        "service_requested": "attended in-lab polysomnography",
        "clinical_notes": (
            "Uncomplicated adult with suspected OSA. Requesting in-lab study as "
            "the initial test."
        ),
        "expected": "route-to-human",
    },
    {
        "case_id": "CASE-011",
        "service_requested": "cardiac stress test",
        "clinical_notes": "8 weeks of chest discomfort; conservative therapy documented.",
        "expected": "route-to-human",
    },
    {
        "case_id": "CASE-012",
        "service_requested": "physical therapy extension",
        "clinical_notes": "Routine follow-up; coverage criteria not clearly documented.",
        "expected": "route-to-human",
    },
]


def main() -> None:
    os.makedirs("data/labeled", exist_ok=True)
    os.makedirs("data/cases", exist_ok=True)
    with open("data/labeled/eval_set.json", "w", encoding="utf-8") as f:
        json.dump(CASES, f, indent=2)
    unlabeled = [{k: v for k, v in c.items() if k != "expected"} for c in CASES]
    with open("data/cases/synthetic_cases.json", "w", encoding="utf-8") as f:
        json.dump(unlabeled, f, indent=2)
    print(f"wrote {len(CASES)} synthetic cases -> data/labeled/eval_set.json")
    print(f"wrote {len(unlabeled)} unlabeled cases -> data/cases/synthetic_cases.json")


if __name__ == "__main__":
    main()
