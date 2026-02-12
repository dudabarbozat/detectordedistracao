from detector.logic import AttentionState, DetectorConfig, FrameSignals
from detector.tracker import AttentionTracker


def test_tracker_accumulates_no_face_seconds() -> None:
    tracker = AttentionTracker(config=DetectorConfig(no_face_seconds_threshold=0.1))

    first = tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None), timestamp_s=0.00)
    second = tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None), timestamp_s=0.12)

    assert first == AttentionState.ATTENTIVE
    assert second == AttentionState.DISTRACTED_NO_FACE


def test_tracker_recovery_hysteresis_prevents_flicker() -> None:
    tracker = AttentionTracker(
        config=DetectorConfig(no_face_seconds_threshold=0.1, recover_seconds_threshold=0.2)
    )

    tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None), timestamp_s=0.00)
    distracted = tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None), timestamp_s=0.12)
    still_distracted = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.5), timestamp_s=0.20)
    recovered = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.5), timestamp_s=0.45)

    assert distracted == AttentionState.DISTRACTED_NO_FACE
    assert still_distracted == AttentionState.DISTRACTED_NO_FACE
    assert recovered == AttentionState.ATTENTIVE


def test_tracker_looking_away_uses_time_threshold() -> None:
    tracker = AttentionTracker(
        config=DetectorConfig(max_center_offset_ratio=0.2, looking_away_seconds_threshold=0.2)
    )

    first = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.85), timestamp_s=0.00)
    second = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.85), timestamp_s=0.25)

    assert first == AttentionState.ATTENTIVE
    assert second == AttentionState.DISTRACTED_LOOKING_AWAY


def test_tracker_resets_eyes_closed_seconds_when_eyes_open() -> None:
    tracker = AttentionTracker(config=DetectorConfig(eyes_closed_seconds_threshold=0.1, recover_seconds_threshold=0.1))

    tracker.update(FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5), timestamp_s=0.0)
    tracker.update(FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5), timestamp_s=0.15)
    recovered = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.5), timestamp_s=0.35)

    assert recovered == AttentionState.ATTENTIVE
    assert tracker.eyes_closed_seconds == 0.0
