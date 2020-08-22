import configparser
import dataclasses as dc
import logging
import os
from pathlib import Path
import re
from typing import Callable, MutableMapping, Union

from atomicwrites import atomic_write

from swtor_settings_updater.util.option_transformer import OptionTransformer


@dc.dataclass
class CharacterMetadata:
    __slots__ = ["server_id", "name"]
    server_id: str
    name: str


UpdateCallback = Callable[[CharacterMetadata, MutableMapping[str, str]], None]


def default_settings_dir() -> Path:
    return Path(os.environ["LOCALAPPDATA"]) / "SWTOR" / "swtor" / "settings"


class Character:
    logger: logging.Logger
    option_transformer: OptionTransformer

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.option_transformer = OptionTransformer()

    def update_all(
        self, settings_dir: Union[str, os.PathLike], callback: UpdateCallback
    ) -> None:
        settings_dir = Path(settings_dir)

        for path in settings_dir.glob("he*_*_PlayerGUIState.ini"):
            self.update_path(path, callback)

    def update_path(
        self, path: Union[str, os.PathLike], callback: UpdateCallback
    ) -> None:
        path = Path(path)

        match = re.fullmatch(
            r"(?P<server_id>he[^_]+)_(?P<character_name>[^_]+)_PlayerGUIState.ini",
            path.name,
        )
        if not match:
            raise ValueError(f"Unrecognized filename: {path!r}")

        metadata = CharacterMetadata(
            server_id=match.group("server_id"), name=match.group("character_name"),
        )

        self.logger.info(f"Updating {metadata.server_id} {metadata.name}")

        parser = self._config_parser()
        parser.read(path, encoding="CP1252")

        callback(metadata, parser["Settings"])

        with atomic_write(path, encoding="CP1252", newline="\r\n", overwrite=True) as f:
            parser.write(f)

    def _config_parser(self) -> configparser.ConfigParser:
        parser = configparser.ConfigParser(interpolation=None)
        self.option_transformer.install(parser)
        return parser
