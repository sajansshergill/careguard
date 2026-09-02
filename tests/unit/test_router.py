from careguard.agents.router import route


def _base(confidence, grounding, draft):
    return {"confidence": confidence, "grounding_rate": grounding, "draft_decision": draft}


def test_confident_grounded_approve_auto_resolves():
    s = route(_base(0.9, 1.0, "approve"))
    assert s["final_decision"] == "approve"
    assert s["escalated"] is False


def test_low_confidence_escalates():
    s = route(_base(0.5, 1.0, "approve"))
    assert s["escalated"] is True
    assert s["final_decision"] == "route-to-human"


def test_ungrounded_escalates_even_if_confident():
    s = route(_base(0.95, 0.5, "deny"))
    assert s["escalated"] is True


def test_route_to_human_draft_never_auto_resolves():
    s = route(_base(0.99, 1.0, "route-to-human"))
    assert s["final_decision"] == "route-to-human"