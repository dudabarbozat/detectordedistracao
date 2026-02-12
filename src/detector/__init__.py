"""Pacote do detector de distração."""

from .logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention
from .tracker import AttentionTracker
from .vision import DetectionOutput, HaarSignalDetector

__all__ = [
    "AttentionState",
    "AttentionTracker",
    "DetectionOutput",
    "DetectorConfig",
    "FrameSignals",
    "HaarSignalDetector",
    "evaluate_attention",
]
