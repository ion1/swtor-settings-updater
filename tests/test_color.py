from typing import Any, Callable, Tuple

from hypothesis import given
import hypothesis.strategies as st
import pytest

from swtor_settings_updater.color import Color


@st.composite
def valid_rgb(draw: Callable[[Any], int]) -> Tuple[int, int, int]:
    r = draw(st.integers(min_value=0, max_value=0xFF))
    g = draw(st.integers(min_value=0, max_value=0xFF))
    b = draw(st.integers(min_value=0, max_value=0xFF))
    return (r, g, b)


@st.composite
def invalid_rgb(draw: Callable[[Any], Any]) -> Tuple[int, int, int]:
    v0 = draw(st.one_of(st.integers(max_value=-1), st.integers(min_value=0x100)))
    v1 = draw(st.integers(min_value=0, max_value=0xFF))
    v2 = draw(st.integers(min_value=0, max_value=0xFF))
    [r, g, b] = draw(st.permutations([v0, v1, v2]))
    return (r, g, b)


@given(valid_rgb())
def test_color_valid(rgb: Tuple[int, int, int]) -> None:
    color = Color(*rgb)
    r, g, b = rgb
    assert color.r == r
    assert color.g == g
    assert color.b == b


@given(invalid_rgb())
def test_color_invalid(rgb: Tuple[int, int, int]) -> None:
    with pytest.raises(ValueError):
        Color(*rgb)


@given(valid_rgb())
def test_color_hex(rgb: Tuple[int, int, int]) -> None:
    r, g, b = rgb
    hex_str = Color(r, g, b).hex()
    assert int(hex_str, 16) == (r << 16) | (g << 8) | b
