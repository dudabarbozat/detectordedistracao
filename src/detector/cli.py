from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

from .logic import AttentionState, DetectorConfig, FrameSignals
from .tracker import AttentionTracker

if TYPE_CHECKING:
    import cv2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detector de distração em tempo real")
    parser.add_argument("--camera", type=int, default=0, help="Índice da câmera (padrão: 0)")
    parser.add_argument("--source", type=str, default=None, help="Arquivo de vídeo para teste (opcional)")
    parser.add_argument("--no-face-threshold", type=int, default=30, help="Frames seguidos sem rosto para alertar")
    parser.add_argument("--eyes-closed-threshold", type=int, default=20, help="Frames seguidos com olhos fechados")
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


def _load_cascades(cv2_module: Any) -> tuple[Any, Any]:
    face_path = cv2_module.data.haarcascades + "haarcascade_frontalface_default.xml"
    eye_path = cv2_module.data.haarcascades + "haarcascade_eye.xml"

    face_cascade = cv2_module.CascadeClassifier(face_path)
    eye_cascade = cv2_module.CascadeClassifier(eye_path)

    if face_cascade.empty() or eye_cascade.empty():
        raise RuntimeError("Não foi possível carregar os classificadores Haar do OpenCV.")

    return face_cascade, eye_cascade


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


def main() -> None:
    args = parse_args()
    config = DetectorConfig(
        no_face_frames_threshold=args.no_face_threshold,
        eyes_closed_frames_threshold=args.eyes_closed_threshold,
        max_center_offset_ratio=args.center_offset_threshold,
    )
    tracker = AttentionTracker(config=config)

    cv2 = _import_cv2()
    face_cascade, eye_cascade = _load_cascades(cv2)

    source = args.source if args.source is not None else args.camera
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir a fonte de vídeo: {source}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

            has_face = len(faces) > 0
            has_eyes = False
            face_center_x_ratio = None

            if has_face:
                x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
                face_center_x_ratio = (x + w / 2) / frame.shape[1]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 180, 0), 2)

                roi_gray = gray[y : y + h, x : x + w]
                roi_color = frame[y : y + h, x : x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))
                has_eyes = len(eyes) >= 1

                for ex, ey, ew, eh in eyes[:2]:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 255), 2)

            signals = FrameSignals(
                has_face=has_face,
                has_eyes=has_eyes,
                face_center_x_ratio=face_center_x_ratio,
            )
            status = tracker.update(signals)

            _put_status(cv2, frame, status)
            cv2.imshow("Detector de Distração", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
