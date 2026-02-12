from detector.logic import AttentionState
from detector.smoothing import TemporalStateSmoother


def test_smoother_returns_recent_state_on_tie() -> None:
    smoother = TemporalStateSmoother(window_size=2)

    smoother.push(AttentionState.ATTENTIVE)
    output = smoother.push(AttentionState.DISTRACTED_NO_FACE)

    assert output == AttentionState.DISTRACTED_NO_FACE


def test_smoother_returns_majority_state_with_window() -> None:
    smoother = TemporalStateSmoother(window_size=5)

    smoother.push(AttentionState.ATTENTIVE)
    smoother.push(AttentionState.DISTRACTED_LOOKING_AWAY)
    smoother.push(AttentionState.ATTENTIVE)
    smoother.push(AttentionState.DISTRACTED_EYES_CLOSED)
    output = smoother.push(AttentionState.ATTENTIVE)

    assert output == AttentionState.ATTENTIVE


def test_smoother_window_size_is_at_least_one() -> None:
    smoother = TemporalStateSmoother(window_size=0)

    output = smoother.push(AttentionState.DISTRACTED_NO_FACE)

    assert output == AttentionState.DISTRACTED_NO_FACE
