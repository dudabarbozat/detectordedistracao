from detector.control import adjust_config_from_key
from detector.logic import DetectorConfig


def test_decrease_no_face_threshold_with_key_1() -> None:
    result = adjust_config_from_key(DetectorConfig(no_face_frames_threshold=5), ord("1"))

    assert result.changed is True
    assert result.config.no_face_frames_threshold == 4


def test_no_face_threshold_has_minimum_value() -> None:
    result = adjust_config_from_key(DetectorConfig(no_face_frames_threshold=1), ord("1"))

    assert result.changed is False
    assert result.config.no_face_frames_threshold == 1


def test_increase_smoothing_window_with_key_8() -> None:
    result = adjust_config_from_key(DetectorConfig(smoothing_window_size=3), ord("8"))

    assert result.changed is True
    assert result.config.smoothing_window_size == 4


def test_ignores_unknown_key() -> None:
    original = DetectorConfig()
    result = adjust_config_from_key(original, ord("x"))

    assert result.changed is False
    assert result.config == original
