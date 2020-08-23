import os
from pathlib import Path


def default_settings_dir() -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "SWTOR"
