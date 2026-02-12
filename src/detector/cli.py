from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

from .logic import AttentionState, DetectorConfig
from .tracker import AttentionTracker
from .vision import HaarSignalDetector

if TYPE_CHECKING:
    import cv2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detector de distração em tempo real")
    parser.add_argument("--camera", type=int, default=0, help="Índice da câmera (padrão: 0)")
    parser.add_argument("--source", type=str, default=None, help="Arquivo de vídeo para teste (opcional)")
    parser.add_argument("--no-face-threshold", type=float, default=1.2, help="Segundos sem rosto para alertar")
    parser.add_argument("--eyes-closed-threshold", type=float, default=0.8, help="Segundos com olhos fechados")
    parser.add_argument("--looking-away-threshold", type=float, default=1.0, help="Segundos olhando para longe")
    parser.add_argument("--recover-threshold", type=float, default=0.4, help="Segundos atentos para sair de alerta")
    parser.add_argument(
        "--center-offset-threshold",
        type=float,
        default=0.30,
        help="Desvio máximo do centro (0 a 0.5) antes de alertar",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)
    return args


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.camera < 0:
        parser.error("--camera deve ser >= 0")

    if args.no_face_threshold <= 0:
        parser.error("--no-face-threshold deve ser > 0")

    if args.eyes_closed_threshold <= 0:
        parser.error("--eyes-closed-threshold deve ser > 0")

    if args.looking_away_threshold <= 0:
        parser.error("--looking-away-threshold deve ser > 0")

    if args.recover_threshold <= 0:
        parser.error("--recover-threshold deve ser > 0")

    if not 0.0 <= args.center_offset_threshold <= 0.5:
        parser.error("--center-offset-threshold deve estar entre 0.0 e 0.5")


def _import_cv2() -> Any:
    try:
        import cv2  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenCV não está instalado. Instale com `pip install opencv-python` "
            "(ou `pip install -e .[dev]`) e tente novamente."
        ) from exc
    return cv2


def _put_status(cv2_module: Any, frame: Any, status: AttentionState) -> None:
    color = (0, 200, 0) if status == AttentionState.ATTENTIVE else (0, 0, 255)
    cv2_module.putText(
        frame,
        f"Estado: {status.value}",
        (20, 35),
        cv2_module.FONT_HERSHEY_SIMPLEX,
        0.9,
        color,
        2,
        cv2_module.LINE_AA,
    )


def _draw_detections(cv2_module: Any, frame: Any, face_box: tuple[int, int, int, int] | None, eye_boxes: list[tuple[int, int, int, int]]) -> None:
    if face_box is not None:
        x, y, w, h = face_box
        cv2_module.rectangle(frame, (x, y), (x + w, y + h), (255, 180, 0), 2)

    for ex, ey, ew, eh in eye_boxes:
        cv2_module.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)


def main() -> None:
    args = parse_args()
    config = DetectorConfig(
        no_face_seconds_threshold=args.no_face_threshold,
        eyes_closed_seconds_threshold=args.eyes_closed_threshold,
        looking_away_seconds_threshold=args.looking_away_threshold,
        recover_seconds_threshold=args.recover_threshold,
        max_center_offset_ratio=args.center_offset_threshold,
    )
    tracker = AttentionTracker(config=config)

    cv2 = _import_cv2()
    detector = HaarSignalDetector(cv2)

    source = args.source if args.source is not None else args.camera
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir a fonte de vídeo: {source}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            detection = detector.detect(frame)
            status = tracker.update(detection.signals)

            _draw_detections(cv2, frame, detection.face_box, detection.eye_boxes)
            _put_status(cv2, frame, status)
            cv2.imshow("Detector de Distração", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
