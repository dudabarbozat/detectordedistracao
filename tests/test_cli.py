import builtins

import pytest

from detector import cli


def test_parse_args_accepts_valid_values() -> None:
    args = cli.parse_args([
        "--camera",
        "1",
        "--no-face-threshold",
        "10",
        "--eyes-closed-threshold",
        "5",
        "--center-offset-threshold",
        "0.2",
    ])

    assert args.camera == 1
    assert args.no_face_threshold == 10
    assert args.eyes_closed_threshold == 5
    assert args.center_offset_threshold == 0.2


@pytest.mark.parametrize(
    "argv",
    [
        ["--camera", "-1"],
        ["--no-face-threshold", "0"],
        ["--eyes-closed-threshold", "0"],
        ["--center-offset-threshold", "0.8"],
        ["--center-offset-threshold", "-0.1"],
    ],
)
def test_parse_args_rejects_invalid_values(argv: list[str]) -> None:
    with pytest.raises(SystemExit):
        cli.parse_args(argv)


def test_import_cv2_returns_friendly_error_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001
        if name == "cv2":
            raise ModuleNotFoundError("No module named 'cv2'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match="OpenCV não está instalado"):
        cli._import_cv2()
