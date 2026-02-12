"""Pacote do detector de distração."""

from .logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention
from .tracker import AttentionTracker

__all__ = [
    "AttentionState",
    "AttentionTracker",
    "DetectorConfig",
    "FrameSignals",
    "evaluate_attention",
]
