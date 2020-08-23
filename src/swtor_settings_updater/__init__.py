from . import character
from .character import CharacterMetadata
from .chat import Chat
from .color import Color
from .util.settings_dir import default_settings_dir


__version__ = "0.0.4"

__all__ = ["character", "CharacterMetadata", "Chat", "Color", "default_settings_dir"]
