from detector.logic import AttentionState, DetectorConfig, FrameSignals
from detector.tracker import AttentionTracker


def test_tracker_accumulates_no_face_frames() -> None:
    tracker = AttentionTracker(config=DetectorConfig(no_face_frames_threshold=2))

    first = tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None))
    second = tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None))

    assert first == AttentionState.ATTENTIVE
    assert second == AttentionState.DISTRACTED_NO_FACE


def test_tracker_resets_no_face_counter_when_face_returns() -> None:
    tracker = AttentionTracker(config=DetectorConfig(no_face_frames_threshold=2))

    tracker.update(FrameSignals(has_face=False, has_eyes=False, face_center_x_ratio=None))
    recovered = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.5))

    assert recovered == AttentionState.ATTENTIVE
    assert tracker.consecutive_no_face_frames == 0


def test_tracker_accumulates_closed_eyes_only_with_face() -> None:
    tracker = AttentionTracker(config=DetectorConfig(eyes_closed_frames_threshold=2))

    first = tracker.update(FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5))
    second = tracker.update(FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5))

    assert first == AttentionState.ATTENTIVE
    assert second == AttentionState.DISTRACTED_EYES_CLOSED


def test_tracker_resets_eyes_counter_when_eyes_open() -> None:
    tracker = AttentionTracker(config=DetectorConfig(eyes_closed_frames_threshold=2))

    tracker.update(FrameSignals(has_face=True, has_eyes=False, face_center_x_ratio=0.5))
    recovered = tracker.update(FrameSignals(has_face=True, has_eyes=True, face_center_x_ratio=0.5))

    assert recovered == AttentionState.ATTENTIVE
    assert tracker.consecutive_eyes_closed_frames == 0
