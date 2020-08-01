from __future__ import annotations
import dataclasses as dc


@dc.dataclass
class Color:
    __slots__ = ["r", "g", "b"]
    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        if not (0 <= self.r <= 0xFF and 0 <= self.g <= 0xFF and 0 <= self.b <= 0xFF):
            raise ValueError(f"Invalid {self!r}")

    def hex(self) -> str:
        """Hexadecimal RRGGBB."""
        return "{:0>2x}{:0>2x}{:0>2x}".format(self.r, self.g, self.b)

    def copy(self) -> Color:
        return dc.replace(self)
