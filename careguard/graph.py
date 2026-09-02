"""LangGraph wiring: retriever -> reasoner -> guardrail -> router."""
from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph

from careguard.agents.guardrail import guard
from careguard.agents.reasoner import reason
from careguard.agents.retriever import retrieve
from careguard.agents.router import route
from careguard.state import CaseState
from careguard.storage.audit import write_audit
from careguard.utils.logging_config import setup_logging
from careguard.utils.timing import timed

setup_logging()
log = logging.getLogger("careguard")


def build_graph():
    g = StateGraph(CaseState)
    g.add_node("retriever", retrieve)
    g.add_node("reasoner", reason)
    g.add_node("guardrail", guard)
    g.add_node("router", route)

    g.add_edge(START, "retriever")
    g.add_edge("retriever", "reasoner")
    g.add_edge("reasoner", "guardrail")
    g.add_edge("guardrail", "router")
    g.add_edge("router", END)
    return g.compile()


_app = build_graph()


def run_case(case: dict) -> CaseState:
    """Entry point used by the API, UI, and eval harness."""
    with timed() as elapsed:
        result: CaseState = _app.invoke(case)
    write_audit(result)
    log.info(
        "case=%s decision=%s conf=%.2f grounding=%.2f latency_ms=%.0f",
        result.get("case_id"),
        result.get("final_decision"),
        result.get("confidence") or 0.0,
        result.get("grounding_rate") or 0.0,
        elapsed(),
    )
    return result
