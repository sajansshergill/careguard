"""Streamlit demo.  streamlit run app.py"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from careguard.graph import run_case
from careguard.utils.citations import format_rationale

st.set_page_config(page_title="CareGuard", page_icon="🛡️", layout="wide")
st.title("CareGuard — Prior Auth Triage")
st.caption("Synthetic data only. Not a clinical or coverage-decision tool.")

EXAMPLES_PATH = Path("data/labeled/eval_set.json")


def _examples() -> list[dict]:
    if EXAMPLES_PATH.exists():
        try:
            return json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return [
        {
            "case_id": "DEMO-001",
            "service_requested": "MRI lumbar spine",
            "clinical_notes": "8 weeks of symptoms; conservative therapy documented.",
        }
    ]


examples = _examples()
labels = [f"{c['case_id']}: {c['service_requested']}" for c in examples]
choice = st.sidebar.selectbox("Load a synthetic example", ["(custom)"] + labels)
st.sidebar.markdown(
    "Auto-decide only when **every claim is grounded** and confidence "
    "clears the threshold. Otherwise the case is routed to a human."
)

if choice != "(custom)":
    selected = examples[labels.index(choice)]
    default_service = selected["service_requested"]
    default_notes = selected["clinical_notes"]
    case_id = selected["case_id"]
else:
    default_service = "MRI lumbar spine"
    default_notes = "8 weeks of symptoms; conservative therapy documented."
    case_id = "DEMO-001"

service = st.text_input("Service requested", default_service)
notes = st.text_area("Clinical notes", default_notes, height=140)

if st.button("Run triage", type="primary"):
    state = run_case(
        {
            "case_id": case_id,
            "service_requested": service,
            "clinical_notes": notes,
        }
    )
    decision = state["final_decision"]
    color = {"approve": "green", "deny": "red", "route-to-human": "orange"}[decision]
    st.markdown(f"### Decision: :{color}[{decision}]")
    c1, c2, c3 = st.columns(3)
    c1.metric("Confidence", f"{state['confidence']:.0%}")
    c2.metric("Grounding", f"{state['grounding_rate']:.0%}")
    c3.metric("Escalated", "yes" if state["escalated"] else "no")
    if state["escalated"]:
        st.info("Low confidence or ungrounded reasoning → routed to a human reviewer.")
    st.subheader("Cited rationale")
    st.code(format_rationale(state), language="text")
    with st.expander("Retrieved policy clauses"):
        for clause in state.get("clauses", []):
            st.markdown(
                f"**`{clause.clause_id}`** · score {clause.score:.2f}  \n{clause.text}"
            )
