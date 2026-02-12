from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AttentionState(str, Enum):
    ATTENTIVE = "atento"
    DISTRACTED_NO_FACE = "distraido_sem_rosto"
    DISTRACTED_EYES_CLOSED = "distraido_olhos_fechados"
    DISTRACTED_LOOKING_AWAY = "distraido_olhando_longe"


@dataclass(frozen=True)
class DetectorConfig:
    no_face_frames_threshold: int = 30
    eyes_closed_frames_threshold: int = 20
    max_center_offset_ratio: float = 0.30


@dataclass(frozen=True)
class RuntimeConfig:
    camera_index: int = 0
    metrics_log_interval_frames: int = 30


@dataclass
class FrameSignals:
    has_face: bool
    has_eyes: bool
    face_center_x_ratio: float | None


@dataclass(frozen=True)
class FrameCounters:
    consecutive_no_face_frames: int = 0
    consecutive_eyes_closed_frames: int = 0


def update_frame_counters(
    counters: FrameCounters,
    has_face: bool,
    has_eyes: bool,
) -> FrameCounters:
    no_face_frames = counters.consecutive_no_face_frames + 1 if not has_face else 0
    eyes_closed_frames = counters.consecutive_eyes_closed_frames + 1 if has_face and not has_eyes else 0
    return FrameCounters(
        consecutive_no_face_frames=no_face_frames,
        consecutive_eyes_closed_frames=eyes_closed_frames,
    )


def evaluate_attention(
    signals: FrameSignals,
    consecutive_no_face_frames: int,
    consecutive_eyes_closed_frames: int,
    config: DetectorConfig,
) -> AttentionState:
    if not signals.has_face:
        if consecutive_no_face_frames >= config.no_face_frames_threshold:
            return AttentionState.DISTRACTED_NO_FACE
        return AttentionState.ATTENTIVE

    if not signals.has_eyes and consecutive_eyes_closed_frames >= config.eyes_closed_frames_threshold:
        return AttentionState.DISTRACTED_EYES_CLOSED

    if signals.face_center_x_ratio is not None:
        center_offset = abs(signals.face_center_x_ratio - 0.5)
        if center_offset > config.max_center_offset_ratio:
            return AttentionState.DISTRACTED_LOOKING_AWAY

    return AttentionState.ATTENTIVE
