import configparser
from typing import Dict


class OptionTransformer:
    """Prevent ConfigParser from lower-casing key names."""

    canonical_forms: Dict[str, str]

    def __init__(self) -> None:
        self.canonical_forms = {}

    def install(self, parser: configparser.ConfigParser) -> None:
        """Replace parser.optionxform with a case-preserving version."""
        # https://github.com/python/mypy/issues/2427
        parser.optionxform = self.xform  # type: ignore[assignment]

    def xform(self, name: str) -> str:
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
