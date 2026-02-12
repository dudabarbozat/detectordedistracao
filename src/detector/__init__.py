"""Pacote do detector de distração."""

from .logic import AttentionState, DetectorConfig, FrameCounters, FrameSignals, RuntimeConfig, evaluate_attention

__all__ = [
    "AttentionState",
    "DetectorConfig",
    "RuntimeConfig",
    "FrameSignals",
    "FrameCounters",
    "evaluate_attention",
]
