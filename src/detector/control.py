from __future__ import annotations

from dataclasses import dataclass

from .logic import DetectorConfig


@dataclass(frozen=True)
class ControlResult:
    config: DetectorConfig
    changed: bool
    message: str | None = None


def adjust_config_from_key(config: DetectorConfig, key_code: int) -> ControlResult:
    key = chr(key_code).lower() if 0 <= key_code <= 255 else ""

    if key == "1":
        value = max(1, config.no_face_frames_threshold - 1)
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=value,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=value != config.no_face_frames_threshold,
            message=f"no_face_frames_threshold={value}",
        )

    if key == "2":
        value = config.no_face_frames_threshold + 1
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=value,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=True,
            message=f"no_face_frames_threshold={value}",
        )

    if key == "3":
        value = max(1, config.eyes_closed_frames_threshold - 1)
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=value,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=value != config.eyes_closed_frames_threshold,
            message=f"eyes_closed_frames_threshold={value}",
        )

    if key == "4":
        value = config.eyes_closed_frames_threshold + 1
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=value,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=True,
            message=f"eyes_closed_frames_threshold={value}",
        )

    if key == "5":
        value = max(0.05, round(config.max_center_offset_ratio - 0.01, 2))
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=value,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=value != config.max_center_offset_ratio,
            message=f"max_center_offset_ratio={value:.2f}",
        )

    if key == "6":
        value = min(0.49, round(config.max_center_offset_ratio + 0.01, 2))
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=value,
                smoothing_window_size=config.smoothing_window_size,
            ),
            changed=value != config.max_center_offset_ratio,
            message=f"max_center_offset_ratio={value:.2f}",
        )

    if key == "7":
        value = max(1, config.smoothing_window_size - 1)
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=value,
            ),
            changed=value != config.smoothing_window_size,
            message=f"smoothing_window_size={value}",
        )

    if key == "8":
        value = config.smoothing_window_size + 1
        return ControlResult(
            config=DetectorConfig(
                no_face_frames_threshold=config.no_face_frames_threshold,
                eyes_closed_frames_threshold=config.eyes_closed_frames_threshold,
                max_center_offset_ratio=config.max_center_offset_ratio,
                smoothing_window_size=value,
            ),
            changed=True,
            message=f"smoothing_window_size={value}",
        )

    return ControlResult(config=config, changed=False)
