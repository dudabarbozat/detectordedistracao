from __future__ import annotations

from dataclasses import dataclass

from .logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention


@dataclass
class AttentionTracker:
    """Rastreia sinais ao longo do tempo para decidir estado de atenção."""

    config: DetectorConfig
    consecutive_no_face_frames: int = 0
    consecutive_eyes_closed_frames: int = 0

    def update(self, signals: FrameSignals) -> AttentionState:
        self.consecutive_no_face_frames = self.consecutive_no_face_frames + 1 if not signals.has_face else 0
        self.consecutive_eyes_closed_frames = (
            self.consecutive_eyes_closed_frames + 1 if signals.has_face and not signals.has_eyes else 0
        )

        return evaluate_attention(
            signals=signals,
            consecutive_no_face_frames=self.consecutive_no_face_frames,
            consecutive_eyes_closed_frames=self.consecutive_eyes_closed_frames,
            config=self.config,
        )
