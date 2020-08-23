from pathlib import Path
from typing import Any

from swtor_settings_updater import default_settings_dir


# TODO: pytest defines MonkeyPatch internally but does not seem to export it.
def test_default_settings_dir(monkeypatch: Any) -> None:
    monkeypatch.setenv("LOCALAPPDATA", "foobar")
    assert default_settings_dir() == Path("foobar/SWTOR")
