from detector.logic import (
    AttentionState,
    DetectorConfig,
    FrameCounters,
    FrameSignals,
    evaluate_attention,
    update_frame_counters,
)


def test_no_face_becomes_distraction_after_threshold() -> None:
    config = DetectorConfig(no_face_frames_threshold=3)
    signals = FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None)

    state = evaluate_attention(signals, consecutive_no_face_frames=3, consecutive_eyes_closed_frames=0, config=config)

    assert state == AttentionState.DISTRACTED_NO_FACE


def test_no_face_below_threshold_stays_attentive() -> None:
    config = DetectorConfig(no_face_frames_threshold=3)
    signals = FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None)

    state = evaluate_attention(signals, consecutive_no_face_frames=2, consecutive_eyes_closed_frames=0, config=config)

    assert state == AttentionState.ATTENTIVE


def test_eyes_closed_becomes_distraction_after_threshold() -> None:
    config = DetectorConfig(eyes_closed_frames_threshold=4)
    signals = FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5)

    state = evaluate_attention(signals, consecutive_no_face_frames=0, consecutive_eyes_closed_frames=4, config=config)

    assert state == AttentionState.DISTRACTED_EYES_CLOSED


def test_face_far_from_center_is_looking_away() -> None:
    config = DetectorConfig(max_center_offset_ratio=0.2)
    signals = FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.85)

    state = evaluate_attention(signals, consecutive_no_face_frames=0, consecutive_eyes_closed_frames=0, config=config)

    assert state == AttentionState.DISTRACTED_LOOKING_AWAY


def test_face_on_exact_center_threshold_is_attentive() -> None:
    config = DetectorConfig(max_center_offset_ratio=0.2)
    signals = FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.7)

    state = evaluate_attention(signals, consecutive_no_face_frames=0, consecutive_eyes_closed_frames=0, config=config)

    assert state == AttentionState.ATTENTIVE


def test_counters_reset_with_intermittent_face_presence() -> None:
    counters = FrameCounters()

    counters = update_frame_counters(counters, has_face=False, has_eyes=False)
    counters = update_frame_counters(counters, has_face=False, has_eyes=False)
    counters = update_frame_counters(counters, has_face=True, has_eyes=True)

    assert counters.consecutive_no_face_frames == 0


def test_eyes_closed_counter_resets_when_face_disappears() -> None:
    counters = FrameCounters()

    counters = update_frame_counters(counters, has_face=True, has_eyes=False)
    counters = update_frame_counters(counters, has_face=False, has_eyes=False)

    assert counters.consecutive_eyes_closed_frames == 0


def test_attentive_when_face_centered_and_eyes_visible() -> None:
    config = DetectorConfig()
    signals = FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.52)

    state = evaluate_attention(signals, consecutive_no_face_frames=0, consecutive_eyes_closed_frames=0, config=config)

    assert state == AttentionState.ATTENTIVE
