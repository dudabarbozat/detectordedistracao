import builtins

import pytest

from detector import cli


def test_parse_args_accepts_valid_values() -> None:
    args = cli.parse_args([
        "--camera",
        "1",
        "--no-face-threshold",
        "1.0",
        "--eyes-closed-threshold",
        "0.5",
        "--looking-away-threshold",
        "0.9",
        "--recover-threshold",
        "0.3",
        "--center-offset-x-threshold",
        "0.2",
        "--center-offset-y-threshold",
        "0.18",
    ])

    assert args.camera == 1
    assert args.no_face_threshold == 1.0
    assert args.eyes_closed_threshold == 0.5
    assert args.looking_away_threshold == 0.9
    assert args.recover_threshold == 0.3
    assert args.center_offset_x_threshold == 0.2
    assert args.center_offset_y_threshold == 0.18


@pytest.mark.parametrize(
    "argv",
    [
        ["--camera", "-1"],
        ["--no-face-threshold", "0"],
        ["--eyes-closed-threshold", "0"],
        ["--looking-away-threshold", "0"],
        ["--recover-threshold", "0"],
        ["--center-offset-x-threshold", "0.8"],
        ["--center-offset-y-threshold", "-0.1"],
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
