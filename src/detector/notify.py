from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Callable
import subprocess
import sys
import webbrowser

from .logic import AttentionState


@dataclass
class DistractionVideoNotifier:
    video_url: str | None
    cooldown_seconds: float = 60.0
    now_provider: Callable[[], float] = monotonic
    opener: Callable[[str], bool] = webbrowser.open_new_tab

    def __post_init__(self) -> None:
        self._last_open_time = -1e9
        self._last_state = AttentionState.ATTENTIVE
        self.last_error: str | None = None

    def _can_open(self) -> bool:
        return bool(self.video_url) and (self.now_provider() - self._last_open_time) >= self.cooldown_seconds

    def _fallback_open(self, url: str) -> bool:
        try:
            if sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            if sys.platform == "darwin":
                subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            if sys.platform.startswith("win"):
                return bool(webbrowser.open(url))
        except OSError as exc:
            self.last_error = f"fallback_open_error: {exc}"
            return False

        self.last_error = "unsupported_platform_for_fallback"
        return False

    def open_now(self) -> bool:
        self.last_error = None

        if not self.video_url:
            self.last_error = "missing_video_url"
            return False

        if not self._can_open():
            self.last_error = "cooldown_active"
            return False

        try:
            if self.opener(self.video_url):
                self._last_open_time = self.now_provider()
                return True
        except Exception as exc:  # noqa: BLE001
            self.last_error = f"primary_open_error: {exc}"

        if self._fallback_open(self.video_url):
            self._last_open_time = self.now_provider()
            return True

        if not self.last_error:
            self.last_error = "open_failed_without_exception"
        return False

    def handle_state(self, state: AttentionState) -> bool:
        if not self.video_url:
            self._last_state = state
            return False

        should_open = state != AttentionState.ATTENTIVE and self._last_state == AttentionState.ATTENTIVE
        self._last_state = state

        if not should_open:
            return False

        return self.open_now()
