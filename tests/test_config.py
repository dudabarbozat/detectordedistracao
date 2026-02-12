from pathlib import Path

from detector.config import load_app_config


def test_load_app_config_with_defaults_when_file_missing(tmp_path: Path) -> None:
    config = load_app_config(str(tmp_path / "missing.toml"))

    assert config.detector.no_face_frames_threshold == 15
    assert config.runtime.camera_index == 0
    assert config.detector.smoothing_window_size == 3


def test_load_app_config_overrides_values_from_toml(tmp_path: Path) -> None:
    config_file = tmp_path / "detector.toml"
    config_file.write_text(
        """
[detector]
no_face_frames_threshold = 10
eyes_closed_frames_threshold = 8
max_center_offset_ratio = 0.25
smoothing_window_size = 7

[runtime]
camera_index = 1
metrics_log_interval_frames = 15
""".strip(),
        encoding="utf-8",
    )

    config = load_app_config(str(config_file))

    assert config.detector.no_face_frames_threshold == 10
    assert config.detector.eyes_closed_frames_threshold == 8
    assert config.detector.max_center_offset_ratio == 0.25
    assert config.detector.smoothing_window_size == 7
    assert config.runtime.camera_index == 1
    assert config.runtime.metrics_log_interval_frames == 15
