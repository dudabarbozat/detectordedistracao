from __future__ import annotations

from collections import Counter, deque

from .logic import AttentionState


class TemporalStateSmoother:
    def __init__(self, window_size: int) -> None:
        self.window_size = max(window_size, 1)
        self._history: deque[AttentionState] = deque(maxlen=self.window_size)

    def push(self, state: AttentionState) -> AttentionState:
        self._history.append(state)
        frequencies = Counter(self._history)
        most_common_count = max(frequencies.values())

        # Critério determinístico em empate: prioriza o estado mais recente entre os mais frequentes.
        for candidate in reversed(self._history):
            if frequencies[candidate] == most_common_count:
                return candidate

        return state
