from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Callable
import webbrowser

from .logic import AttentionState


@dataclass
class DistractionVideoNotifier:
    video_url: str | None
    cooldown_seconds: float = 60.0
    now_provider: Callable[[], float] = monotonic
    opener: Callable[[str], bool] = webbrowser.open

    def __post_init__(self) -> None:
        self._last_open_time = -1e9
        self._last_state = AttentionState.ATTENTIVE

    def handle_state(self, state: AttentionState) -> bool:
        if not self.video_url:
            self._last_state = state
            return False

        should_open = (
            state != AttentionState.ATTENTIVE
            and self._last_state == AttentionState.ATTENTIVE
            and (self.now_provider() - self._last_open_time) >= self.cooldown_seconds
        )

        self._last_state = state
        if not should_open:
            return False

        if self.opener(self.video_url):
            self._last_open_time = self.now_provider()
            return True

        return False
