from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from time import monotonic
from typing import Callable

from .logic import AttentionState


@dataclass
class DistractionVideoNotifier:
    video_url: str | None
    cooldown_seconds: float = 60.0
    now_provider: Callable[[], float] = monotonic
    opener: Callable[[str], bool] = webbrowser.open_new_tab
    command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run
    env_getter: Callable[[str], str | None] = os.getenv

    def __post_init__(self) -> None:
        self._last_open_time = -1e9
        self._last_state = AttentionState.ATTENTIVE
        self.last_error: str | None = None

    def _can_open(self) -> bool:
        return bool(self.video_url) and (self.now_provider() - self._last_open_time) >= self.cooldown_seconds

    def _is_headless_linux(self) -> bool:
        if not sys.platform.startswith("linux"):
            return False
        has_display = bool(self.env_getter("DISPLAY")) or bool(self.env_getter("WAYLAND_DISPLAY"))
        return not has_display

    def _fallback_open(self, url: str) -> bool:
        if sys.platform.startswith("linux"):
            if self._is_headless_linux():
                self.last_error = "headless_environment_missing_display"
                return False
            cmd = ["xdg-open", url]
        elif sys.platform == "darwin":
            cmd = ["open", url]
        elif sys.platform.startswith("win"):
            return bool(webbrowser.open(url))
        else:
            self.last_error = "unsupported_platform_for_fallback"
            return False

        try:
            result = self.command_runner(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except FileNotFoundError:
            self.last_error = f"fallback_command_missing:{cmd[0]}"
            return False
        except subprocess.TimeoutExpired:
            self.last_error = f"fallback_command_timeout:{cmd[0]}"
            return False
        except OSError as exc:
            self.last_error = f"fallback_open_error:{exc}"
            return False

        if result.returncode != 0:
            stderr = (result.stderr or "").strip().replace("\n", " ")[:200]
            self.last_error = f"fallback_command_failed:{cmd[0]}:{result.returncode}:{stderr}"
            return False

        return True

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
            self.last_error = f"primary_open_error:{exc}"

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
