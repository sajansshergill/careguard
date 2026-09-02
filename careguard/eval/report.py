"""Render eval metrics to console, JSON, and a standalone HTML report."""
from __future__ import annotations

import json
import os


def render(summary: dict, rows: list[dict] | None = None) -> None:
    print("\n=== CareGuard Evaluation ===")
    for key, value in summary.items():
        print(f"{key:>22}: {value}")

    os.makedirs("data", exist_ok=True)
    payload = {"metrics": summary, "cases": rows or []}
    with open("data/eval_report.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    _write_html("data/eval_report.html", summary, rows or [])
    print("\nsaved -> data/eval_report.json")
    print("saved -> data/eval_report.html")


def _write_html(path: str, summary: dict, rows: list[dict]) -> None:
    cells = "".join(
        f"<tr><th>{key}</th><td>{value}</td></tr>" for key, value in summary.items()
    )
    body_rows = "".join(
        "<tr>"
        + "".join(f"<td>{_esc(r.get(k, ''))}</td>" for k in _CASE_COLS)
        + "</tr>"
        for r in rows
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>CareGuard eval report</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; color: #111; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #f4f4f5; }}
  </style>
</head>
<body>
  <h1>CareGuard evaluation</h1>
  <table>{cells}</table>
  <h2>Cases</h2>
  <table>
    <thead><tr>{''.join(f'<th>{c}</th>' for c in _CASE_COLS)}</tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


_CASE_COLS = (
    "case_id",
    "expected",
    "final_decision",
    "grounding",
    "hallucination",
    "escalated",
    "correct",
    "judge_score",
    "latency_ms",
)


def _esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
