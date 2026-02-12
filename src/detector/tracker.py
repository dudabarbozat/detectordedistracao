from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from .logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention


@dataclass
class AttentionTracker:
    """Rastreia sinais ao longo do tempo para decidir estado de atenção."""

    config: DetectorConfig
    no_face_seconds: float = 0.0
    eyes_closed_seconds: float = 0.0
    looking_away_seconds: float = 0.0
    attentive_seconds: float = 0.0
    current_state: AttentionState = AttentionState.ATTENTIVE
    _last_timestamp: float | None = None

    def update(self, signals: FrameSignals, timestamp_s: float | None = None) -> AttentionState:
        now = monotonic() if timestamp_s is None else timestamp_s
        dt = self._compute_dt(now)

        self.no_face_seconds = self.no_face_seconds + dt if not signals.has_face else 0.0
        self.eyes_closed_seconds = self.eyes_closed_seconds + dt if signals.has_face and not signals.has_eyes else 0.0

        is_looking_away = False
        if signals.face_center_x_ratio is not None and signals.has_face:
            center_offset = abs(signals.face_center_x_ratio - 0.5)
            is_looking_away = center_offset > self.config.max_center_offset_ratio
        self.looking_away_seconds = self.looking_away_seconds + dt if is_looking_away else 0.0

        raw_state = evaluate_attention(
            signals=signals,
            no_face_seconds=self.no_face_seconds,
            eyes_closed_seconds=self.eyes_closed_seconds,
            looking_away_seconds=self.looking_away_seconds,
            config=self.config,
        )

        if raw_state == AttentionState.ATTENTIVE:
            self.attentive_seconds += dt
            if self.current_state != AttentionState.ATTENTIVE and self.attentive_seconds < self.config.recover_seconds_threshold:
                return self.current_state
            self.current_state = AttentionState.ATTENTIVE
            return self.current_state

        self.attentive_seconds = 0.0
        self.current_state = raw_state
        return self.current_state

    def _compute_dt(self, now: float) -> float:
        if self._last_timestamp is None:
            self._last_timestamp = now
            return 1 / 30

        dt = max(now - self._last_timestamp, 1e-3)
        self._last_timestamp = now
        return dt
