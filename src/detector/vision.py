from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .logic import FrameSignals


@dataclass
class DetectionOutput:
    signals: FrameSignals
    face_box: tuple[int, int, int, int] | None
    eye_boxes: list[tuple[int, int, int, int]]


class AttentionSignalDetector(Protocol):
    def detect(self, frame: Any) -> DetectionOutput:
        ...


class HaarSignalDetector:
    """Backend de detecção baseado em Haar Cascades."""

    def __init__(self, cv2_module: Any) -> None:
        self.cv2 = cv2_module
        face_path = cv2_module.data.haarcascades + "haarcascade_frontalface_default.xml"
        eye_path = cv2_module.data.haarcascades + "haarcascade_eye.xml"

        self.face_cascade = cv2_module.CascadeClassifier(face_path)
        self.eye_cascade = cv2_module.CascadeClassifier(eye_path)

        if self.face_cascade.empty() or self.eye_cascade.empty():
            raise RuntimeError("Não foi possível carregar os classificadores Haar do OpenCV.")

    def detect(self, frame: Any) -> DetectionOutput:
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

        has_face = len(faces) > 0
        has_eyes = False
        face_center_x_ratio = None
        face_center_y_ratio = None
        face_box = None
        eye_boxes: list[tuple[int, int, int, int]] = []

        if has_face:
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            face_box = (x, y, w, h)
            face_center_x_ratio = (x + w / 2) / frame.shape[1]
            face_center_y_ratio = (y + h / 2) / frame.shape[0]

            roi_gray = gray[y : y + h, x : x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))
            has_eyes = len(eyes) >= 1

            for ex, ey, ew, eh in eyes[:2]:
                eye_boxes.append((x + ex, y + ey, ew, eh))

        return DetectionOutput(
            signals=FrameSignals(
                has_face=has_face,
                has_eyes=has_eyes,
                face_center_x_ratio=face_center_x_ratio,
                face_center_y_ratio=face_center_y_ratio,
            ),
            face_box=face_box,
            eye_boxes=eye_boxes,
        )
