from careguard.utils.confidence import aggregate_confidence


def test_grounding_caps_confidence():
    # llm is sure (0.9) but only half grounded -> capped at 0.5
    assert aggregate_confidence(0.5, 0.9) == 0.5


def test_takes_lower_of_the_two():
    assert aggregate_confidence(0.95, 0.7) == 0.7


def test_bounds():
    assert 0.0 <= aggregate_confidence(0.0, 0.0) <= 1.0