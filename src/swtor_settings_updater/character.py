from atomicwrites import atomic_write
import configparser
import glob
import logging
import os
import os.path
import re


SETTINGS_DIR = "%LOCALAPPDATA%/SWTOR/swtor/settings"


class Character:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.option_transformer = OptionTransformer()

    def update_all(self, settings_dir, callback):
        settings_pattern = os.path.join(
            os.path.expandvars(settings_dir), "he*_PlayerGUIState.ini"
        )

        for path in glob.iglob(settings_pattern):
            self.update_path(path, callback)

    def update_path(self, path, callback):
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

    def _config_parser(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = self.option_transformer.xform
        return parser


class OptionTransformer:
    """Prevent ConfigParser from lower-casing key names."""

    def __init__(self):
        self.canonical_forms = {}

    def xform(self, name):
        name_lower = name.lower()

        if name_lower in self.canonical_forms:
            return self.canonical_forms[name_lower]

        elif name == name_lower:
            # A lower-case name, possibly mangled by ConfigParser previously. Do not
            # add it to the dict.
            return name

        else:
            # Add the name to the dict as the canonical form.
            self.canonical_forms[name_lower] = name
            return name
