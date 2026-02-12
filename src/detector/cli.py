from __future__ import annotations

import cv2

from .logic import AttentionState, DetectorConfig, FrameSignals, evaluate_attention


def _load_cascades() -> tuple[cv2.CascadeClassifier, cv2.CascadeClassifier]:
    face_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"

    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade = cv2.CascadeClassifier(eye_path)

    if face_cascade.empty() or eye_cascade.empty():
        raise RuntimeError("Não foi possível carregar os classificadores Haar do OpenCV.")

    return face_cascade, eye_cascade


def _put_status(frame, status: AttentionState) -> None:
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


def main() -> None:
    config = DetectorConfig()
    face_cascade, eye_cascade = _load_cascades()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Não foi possível abrir a webcam.")

    consecutive_no_face_frames = 0
    consecutive_eyes_closed_frames = 0

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

            consecutive_no_face_frames = consecutive_no_face_frames + 1 if not has_face else 0
            consecutive_eyes_closed_frames = consecutive_eyes_closed_frames + 1 if has_face and not has_eyes else 0

            signals = FrameSignals(
                has_face=has_face,
                has_eyes=has_eyes,
                face_center_x_ratio=face_center_x_ratio,
            )
            status = evaluate_attention(
                signals=signals,
                consecutive_no_face_frames=consecutive_no_face_frames,
                consecutive_eyes_closed_frames=consecutive_eyes_closed_frames,
                config=config,
            )

            _put_status(frame, status)
            cv2.imshow("Detector de Distração", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
