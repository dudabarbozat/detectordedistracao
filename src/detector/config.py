from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tomli

from .logic import DetectorConfig, RuntimeConfig


@dataclass(frozen=True)
class AppConfig:
    detector: DetectorConfig
    runtime: RuntimeConfig


def _read_optional_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as file:
        return tomli.load(file)


def load_app_config(config_path: str | None) -> AppConfig:
    file_data = _read_optional_toml(Path(config_path)) if config_path else {}
    detector_data = file_data.get("detector", {})
    runtime_data = file_data.get("runtime", {})

    detector = DetectorConfig(
        no_face_frames_threshold=detector_data.get("no_face_frames_threshold", DetectorConfig.no_face_frames_threshold),
        eyes_closed_frames_threshold=detector_data.get(
            "eyes_closed_frames_threshold",
            DetectorConfig.eyes_closed_frames_threshold,
        ),
        max_center_offset_ratio=detector_data.get("max_center_offset_ratio", DetectorConfig.max_center_offset_ratio),
        smoothing_window_size=detector_data.get("smoothing_window_size", DetectorConfig.smoothing_window_size),
    )

    runtime = RuntimeConfig(
        camera_index=runtime_data.get("camera_index", RuntimeConfig.camera_index),
        metrics_log_interval_frames=runtime_data.get(
            "metrics_log_interval_frames",
            RuntimeConfig.metrics_log_interval_frames,
        ),
    )

    return AppConfig(detector=detector, runtime=runtime)
