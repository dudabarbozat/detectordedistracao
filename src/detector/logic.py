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
    no_face_seconds_threshold: float = 1.2
    eyes_closed_seconds_threshold: float = 0.8
    looking_away_seconds_threshold: float = 1.0
    recover_seconds_threshold: float = 0.4
    max_center_offset_ratio: float = 0.30


@dataclass
class FrameSignals:
    has_face: bool
    has_eyes: bool
    face_center_x_ratio: float | None


def evaluate_attention(
    signals: FrameSignals,
    no_face_seconds: float,
    eyes_closed_seconds: float,
    looking_away_seconds: float,
    config: DetectorConfig,
) -> AttentionState:
    if not signals.has_face:
        if no_face_seconds >= config.no_face_seconds_threshold:
            return AttentionState.DISTRACTED_NO_FACE
        return AttentionState.ATTENTIVE

    if not signals.has_eyes and eyes_closed_seconds >= config.eyes_closed_seconds_threshold:
        return AttentionState.DISTRACTED_EYES_CLOSED

    if signals.face_center_x_ratio is not None:
        center_offset = abs(signals.face_center_x_ratio - 0.5)
        if center_offset > config.max_center_offset_ratio and looking_away_seconds >= config.looking_away_seconds_threshold:
            return AttentionState.DISTRACTED_LOOKING_AWAY

    return AttentionState.ATTENTIVE
