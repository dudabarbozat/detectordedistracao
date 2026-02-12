from __future__ import annotations

import argparse
import logging

import cv2

from .config import load_app_config
from .notify import DistractionVideoNotifier
from .pipeline import DetectorPipeline, draw_runtime_controls, draw_status

DEFAULT_DISTRACTION_VIDEO_URL = "https://www.youtube.com/shorts/3tSGAhyQAKA"


def _load_cascades() -> tuple[cv2.CascadeClassifier, cv2.CascadeClassifier]:
    face_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"

    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade = cv2.CascadeClassifier(eye_path)

    if face_cascade.empty() or eye_cascade.empty():
        raise RuntimeError("Não foi possível carregar os classificadores Haar do OpenCV.")

    return face_cascade, eye_cascade


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detector de distração em tempo real.")
    parser.add_argument("--config", default="detector.toml", help="Caminho para arquivo de configuração TOML.")
    parser.add_argument("--log-level", default="INFO", help="Nível de log (DEBUG, INFO, WARNING, ERROR).")
    parser.add_argument(
        "--distraction-video-url",
        default=DEFAULT_DISTRACTION_VIDEO_URL,
        help="URL (ex.: YouTube) para abrir ao detectar distração.",
    )
    parser.add_argument("--video-cooldown-seconds", type=float, default=60.0, help="Cooldown mínimo entre aberturas do vídeo.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s %(message)s")

    app_config = load_app_config(args.config)
    face_cascade, eye_cascade = _load_cascades()

    pipeline = DetectorPipeline(
        face_cascade=face_cascade,
        eye_cascade=eye_cascade,
        detector_config=app_config.detector,
        metrics_log_interval_frames=app_config.runtime.metrics_log_interval_frames,
    )

    notifier = DistractionVideoNotifier(
        video_url=args.distraction_video_url,
        cooldown_seconds=max(args.video_cooldown_seconds, 0.0),
    )

    cap = cv2.VideoCapture(app_config.runtime.camera_index)
    if not cap.isOpened():
        raise RuntimeError("Não foi possível abrir a webcam.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            inference_result = pipeline.infer_signals(frame)
            status = pipeline.post_process(inference_result.signals)
            draw_status(inference_result.frame, status)
            draw_runtime_controls(inference_result.frame, pipeline.detector_config)
            logger = logging.getLogger(__name__)
            if notifier.handle_state(status):
                logger.info("video_aberto_em_distraction url=%s", args.distraction_video_url)
            pipeline.log_metrics()

            cv2.imshow("Detector de Distração", inference_result.frame)
            key_code = cv2.waitKey(1) & 0xFF
            if key_code == ord("q"):
                break
            if key_code == ord("v"):
                if notifier.open_now():
                    logger.info("video_aberto_em_teste_manual url=%s", args.distraction_video_url)
                else:
                    logger.warning("falha_ao_abrir_video_teste url=%s cooldown=%.1fs", args.distraction_video_url, args.video_cooldown_seconds)
                continue
            pipeline.apply_realtime_control(key_code)
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
