"""Pacote do detector de distração."""

from .logic import AttentionState, DetectorConfig, FrameCounters, FrameSignals, RuntimeConfig, evaluate_attention
from .smoothing import TemporalStateSmoother
from .control import adjust_config_from_key

__all__ = [
    "AttentionState",
    "DetectorConfig",
    "RuntimeConfig",
    "FrameSignals",
    "FrameCounters",
    "evaluate_attention",
    "TemporalStateSmoother",
    "adjust_config_from_key",
]
