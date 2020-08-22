import os
from pathlib import Path

from . import character
from .character import CharacterMetadata
from .chat import Chat
from .color import Color


__version__ = "0.0.4"

__all__ = ["character", "CharacterMetadata", "Chat", "Color", "default_settings_dir"]


def default_settings_dir() -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "SWTOR"
