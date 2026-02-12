from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AttentionState(str, Enum):
    ATTENTIVE = "atento"
    DISTRACTED_NO_FACE = "distraido_sem_rosto"
    DISTRACTED_EYES_CLOSED = "distraido_olhos_fechados"
    DISTRACTED_LOOKING_LEFT = "distraido_olhando_esquerda"
    DISTRACTED_LOOKING_RIGHT = "distraido_olhando_direita"
    DISTRACTED_LOOKING_UP = "distraido_olhando_cima"
    DISTRACTED_LOOKING_DOWN = "distraido_olhando_baixo"


@dataclass(frozen=True)
class DetectorConfig:
    no_face_seconds_threshold: float = 1.2
    eyes_closed_seconds_threshold: float = 0.8
    looking_away_seconds_threshold: float = 0.6
    recover_seconds_threshold: float = 0.4
    max_center_offset_x_ratio: float = 0.22
    max_center_offset_y_ratio: float = 0.20


@dataclass
class FrameSignals:
    has_face: bool
    has_eyes: bool
    face_center_x_ratio: float | None
    face_center_y_ratio: float | None


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

    if signals.face_center_x_ratio is None or signals.face_center_y_ratio is None:
        return AttentionState.ATTENTIVE

    dx = signals.face_center_x_ratio - 0.5
    dy = signals.face_center_y_ratio - 0.5

    is_horiz_away = abs(dx) > config.max_center_offset_x_ratio
    is_vert_away = abs(dy) > config.max_center_offset_y_ratio

    if (is_horiz_away or is_vert_away) and looking_away_seconds >= config.looking_away_seconds_threshold:
        if abs(dx) >= abs(dy):
            return AttentionState.DISTRACTED_LOOKING_RIGHT if dx > 0 else AttentionState.DISTRACTED_LOOKING_LEFT
        return AttentionState.DISTRACTED_LOOKING_DOWN if dy > 0 else AttentionState.DISTRACTED_LOOKING_UP

    return AttentionState.ATTENTIVE
