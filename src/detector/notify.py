from __future__ import annotations

from dataclasses import dataclass
import logging
import platform
import subprocess
from shutil import which
from time import monotonic
from typing import Callable
import webbrowser

from .logic import AttentionState


logger = logging.getLogger(__name__)


def open_video_url(url: str) -> bool:
    if webbrowser.open(url, new=1, autoraise=True):
        return True

    commands_by_platform = {
        "Darwin": ["open", url],
        "Linux": ["xdg-open", url],
        "Windows": ["cmd", "/c", "start", "", url],
    }
    command = commands_by_platform.get(platform.system())
    if command is None or which(command[0]) is None:
        logger.warning("Nenhum comando de abertura de URL disponível para o sistema atual.")
        return False

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, subprocess.SubprocessError):
        logger.warning("Falha ao abrir URL com fallback do sistema.", exc_info=True)
        return False


@dataclass
class DistractionVideoNotifier:
    video_url: str | None
    cooldown_seconds: float = 60.0
    blink_frames_threshold: int = 3
    now_provider: Callable[[], float] = monotonic
    opener: Callable[[str], bool] = open_video_url

    def __post_init__(self) -> None:
        self._last_open_time = -1e9
        self._last_state = AttentionState.ATTENTIVE
        self._last_triggered = False

    def handle_detection(
        self,
        state: AttentionState,
        no_face_frames: int,
        eyes_closed_frames: int,
        no_face_threshold: int,
        eyes_closed_threshold: int,
    ) -> bool:
        if not self.video_url:
            self._last_state = state
            self._last_triggered = False
            return False

        eyes_closed_over_blink = eyes_closed_frames >= max(1, self.blink_frames_threshold)
        thresholds_triggered = (
            no_face_frames >= max(1, no_face_threshold)
            or eyes_closed_frames >= max(1, eyes_closed_threshold)
            or state == AttentionState.DISTRACTED_LOOKING_AWAY
        )
        triggered = eyes_closed_over_blink or thresholds_triggered

        should_open = (
            triggered
            and not self._last_triggered
            and (self.now_provider() - self._last_open_time) >= self.cooldown_seconds
        )

        self._last_state = state
        self._last_triggered = triggered
        if not should_open:
            return False

        if self.opener(self.video_url):
            self._last_open_time = self.now_provider()
            return True

        return False

    def handle_state(self, state: AttentionState) -> bool:
        return self.handle_detection(
            state=state,
            no_face_frames=0,
            eyes_closed_frames=0,
            no_face_threshold=1,
            eyes_closed_threshold=1,
        )
