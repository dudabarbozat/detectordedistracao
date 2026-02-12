from detector.logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention


def test_no_face_becomes_distraction_after_threshold() -> None:
    config = DetectorConfig(no_face_seconds_threshold=0.3)
    signals = FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None)

    state = evaluate_attention(
        signals,
        no_face_seconds=0.3,
        eyes_closed_seconds=0.0,
        looking_away_seconds=0.0,
        config=config,
    )

    assert state == AttentionState.DISTRACTED_NO_FACE


def test_eyes_closed_becomes_distraction_after_threshold() -> None:
    config = DetectorConfig(eyes_closed_seconds_threshold=0.4)
    signals = FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5)

    state = evaluate_attention(
        signals,
        no_face_seconds=0.0,
        eyes_closed_seconds=0.4,
        looking_away_seconds=0.0,
        config=config,
    )

    assert state == AttentionState.DISTRACTED_EYES_CLOSED


def test_face_far_from_center_is_looking_away_after_time_threshold() -> None:
    config = DetectorConfig(max_center_offset_ratio=0.2, looking_away_seconds_threshold=0.5)
    signals = FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.85)

    state = evaluate_attention(
        signals,
        no_face_seconds=0.0,
        eyes_closed_seconds=0.0,
        looking_away_seconds=0.5,
        config=config,
    )

    assert state == AttentionState.DISTRACTED_LOOKING_AWAY


def test_attentive_when_face_centered_and_eyes_visible() -> None:
    config = DetectorConfig()
    signals = FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.52)

    state = evaluate_attention(
        signals,
        no_face_seconds=0.0,
        eyes_closed_seconds=0.0,
        looking_away_seconds=0.0,
        config=config,
    )

    assert state == AttentionState.ATTENTIVE
