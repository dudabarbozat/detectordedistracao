from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter

import cv2

from .logic import AttentionState, DetectorConfig, FrameCounters, FrameSignals, update_frame_counters

LOGGER = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    frame: cv2.typing.MatLike
    signals: FrameSignals


class DetectorPipeline:
    def __init__(
        self,
        face_cascade: cv2.CascadeClassifier,
        eye_cascade: cv2.CascadeClassifier,
        detector_config: DetectorConfig,
        metrics_log_interval_frames: int,
    ) -> None:
        self.face_cascade = face_cascade
        self.eye_cascade = eye_cascade
        self.detector_config = detector_config
        self.metrics_log_interval_frames = max(metrics_log_interval_frames, 1)
        self.counters = FrameCounters()
        self.frame_count = 0
        self.start_time = perf_counter()

    def infer_signals(self, frame: cv2.typing.MatLike) -> InferenceResult:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

        has_face = len(faces) > 0
        has_eyes = False
        face_center_x_ratio = None

        if has_face:
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            face_center_x_ratio = (x + w / 2) / frame.shape[1]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 180, 0), 2)

            roi_gray = gray[y : y + h, x : x + w]
            roi_color = frame[y : y + h, x : x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))
            has_eyes = len(eyes) >= 1

            for ex, ey, ew, eh in eyes[:2]:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)

        signals = FrameSignals(has_face=has_face, has_eyes=has_eyes, face_center_x_ratio=face_center_x_ratio)
        return InferenceResult(frame=frame, signals=signals)

    def post_process(self, signals: FrameSignals) -> AttentionState:
        self.counters = update_frame_counters(self.counters, has_face=signals.has_face, has_eyes=signals.has_eyes)
        return self._evaluate(signals)

    def _evaluate(self, signals: FrameSignals) -> AttentionState:
        from .logic import evaluate_attention

        return evaluate_attention(
            signals=signals,
            consecutive_no_face_frames=self.counters.consecutive_no_face_frames,
            consecutive_eyes_closed_frames=self.counters.consecutive_eyes_closed_frames,
            config=self.detector_config,
        )

    def log_metrics(self) -> None:
        self.frame_count += 1
        if self.frame_count % self.metrics_log_interval_frames != 0:
            return

        elapsed = perf_counter() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0.0
        LOGGER.info(
            "metrics frame_count=%s fps=%.2f no_face_frames=%s eyes_closed_frames=%s",
            self.frame_count,
            fps,
            self.counters.consecutive_no_face_frames,
            self.counters.consecutive_eyes_closed_frames,
        )


def draw_status(frame: cv2.typing.MatLike, status: AttentionState) -> None:
    color = (0, 200, 0) if status == AttentionState.ATTENTIVE else (0, 0, 255)
    cv2.putText(
        frame,
        f"Estado: {status.value}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2,
        cv2.LINE_AA,
    )
