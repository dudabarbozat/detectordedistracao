from detector.logic import AttentionState
from detector.notify import DistractionVideoNotifier


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def now(self) -> float:
        return self.value


class FakeOpener:
    def __init__(self) -> None:
        self.urls: list[str] = []

    def __call__(self, url: str) -> bool:
        self.urls.append(url)
        return True


def test_notifier_opens_on_transition_to_distracted() -> None:
    clock = FakeClock()
    opener = FakeOpener()
    notifier = DistractionVideoNotifier(
        video_url="https://youtube.com/watch?v=test",
        cooldown_seconds=10.0,
        now_provider=clock.now,
        opener=opener,
    )

    assert notifier.handle_state(AttentionState.ATTENTIVE) is False
    assert notifier.handle_state(AttentionState.DISTRACTED_NO_FACE) is True
    assert opener.urls == ["https://youtube.com/watch?v=test"]


def test_notifier_respects_cooldown_between_episodes() -> None:
    clock = FakeClock()
    opener = FakeOpener()
    notifier = DistractionVideoNotifier(
        video_url="https://youtube.com/watch?v=test",
        cooldown_seconds=10.0,
        now_provider=clock.now,
        opener=opener,
    )

    notifier.handle_state(AttentionState.DISTRACTED_NO_FACE)
    notifier.handle_state(AttentionState.ATTENTIVE)
    clock.value = 5.0
    assert notifier.handle_state(AttentionState.DISTRACTED_EYES_CLOSED) is False

    clock.value = 11.0
    notifier.handle_state(AttentionState.ATTENTIVE)
    assert notifier.handle_state(AttentionState.DISTRACTED_LOOKING_AWAY) is True
    assert len(opener.urls) == 2


def test_notifier_allows_manual_open_for_testing() -> None:
    clock = FakeClock()
    opener = FakeOpener()
    notifier = DistractionVideoNotifier(
        video_url="https://youtube.com/watch?v=test",
        cooldown_seconds=10.0,
        now_provider=clock.now,
        opener=opener,
    )

    assert notifier.open_now() is True
    clock.value = 1.0
    assert notifier.open_now() is False


def test_notifier_ignores_when_url_is_missing() -> None:
    notifier = DistractionVideoNotifier(video_url=None)

    assert notifier.handle_state(AttentionState.DISTRACTED_NO_FACE) is False
    assert notifier.open_now() is False
