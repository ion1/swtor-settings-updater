import configparser
import dataclasses as dc
import logging
import os
import re
from pathlib import Path
from typing import Callable
from typing import MutableMapping
from typing import Union

from atomicwrites import atomic_write

from swtor_settings_updater.util.option_transformer import OptionTransformer


@dc.dataclass
class CharacterMetadata:
    __slots__ = ["environment", "server_id", "name"]
    environment: str
    server_id: str
    name: str


UpdateCallback = Callable[[CharacterMetadata, MutableMapping[str, str]], None]


logger = logging.getLogger(__name__)


def update_all(settings_dir: Union[str, os.PathLike], callback: UpdateCallback) -> None:
    settings_dir = Path(settings_dir)

    for path in settings_dir.glob("*/settings/he*_*_PlayerGUIState.ini"):
        update_path(path, callback)


def update_path(path: Union[str, os.PathLike], callback: UpdateCallback) -> None:
    path = Path(path)

    # Examples:
    # .../SWTOR/swtor/settings/he4242_Kai Zykken_PlayerGUIState.ini
    # .../SWTOR/publictest/settings/he4343_Plagueis_PlayerGUIState.ini

    environment = path.parent.parent.name

    match = re.fullmatch(
        r"(?P<server_id>he[^_]+)_(?P<character_name>[^_]+)_PlayerGUIState.ini",
        path.name,
    )
    if not match:
        raise ValueError(f"Unrecognized filename: {path!r}")

    metadata = CharacterMetadata(
        environment=environment,
        server_id=match.group("server_id"),
        name=match.group("character_name"),
    )

    logger.info(f"Updating {metadata.environment} {metadata.server_id} {metadata.name}")

    parser = configparser.ConfigParser(interpolation=None)
    OptionTransformer().install(parser)

    parser.read(path, encoding="CP1252")

    callback(metadata, parser["Settings"])

    with atomic_write(path, encoding="CP1252", newline="\r\n", overwrite=True) as f:
        parser.write(f)
