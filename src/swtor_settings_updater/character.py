from atomicwrites import atomic_write
import configparser
import glob
import logging
import os
import os.path
import re
from typing import Callable, MutableMapping

from swtor_settings_updater.util.option_transformer import OptionTransformer


UpdateCallback = Callable[[str, str, MutableMapping[str, str]], None]

SETTINGS_DIR = "%LOCALAPPDATA%/SWTOR/swtor/settings"


class Character:
    logger: logging.Logger
    option_transformer: OptionTransformer

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.option_transformer = OptionTransformer()

    def update_all(self, settings_dir: str, callback: UpdateCallback) -> None:
        settings_pattern = os.path.join(
            os.path.expandvars(settings_dir), "he*_PlayerGUIState.ini"
        )

        for path in glob.iglob(settings_pattern):
            self.update_path(path, callback)

    def update_path(self, path: str, callback: UpdateCallback) -> None:
        filename = os.path.basename(path)

        match = re.fullmatch(
            r"(?P<server_id>he[^_]+)_(?P<character_name>[^_]+)_PlayerGUIState.ini",
            filename,
        )
        if not match:
            raise ValueError(f"Unrecognized filename: {filename!r}")

        server_id = match.group("server_id")
        character_name = match.group("character_name")

        self.logger.info(f"Updating {server_id} {character_name}")

        parser = self._config_parser()
        parser.read(path, encoding="CP1252")

        callback(server_id, character_name, parser["Settings"])

        with atomic_write(path, encoding="CP1252", newline="\r\n", overwrite=True) as f:
            parser.write(f)

    def _config_parser(self) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None)
        self.option_transformer.install(parser)
        return parser
