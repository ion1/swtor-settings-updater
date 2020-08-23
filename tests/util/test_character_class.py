import codecs
import unicodedata
from typing import Any
from typing import Callable
from typing import Tuple

import hypothesis.strategies as st
import pytest
import regex
from hypothesis import assume
from hypothesis import given

from swtor_settings_updater.util.character_class import CP1252_PRINTABLE
from swtor_settings_updater.util.character_class import regex_character_class


def test_cp1252_printable_encodes_as_cp1252() -> None:
    assert (
        codecs.decode(codecs.encode(CP1252_PRINTABLE, "CP1252"), "CP1252")
        == CP1252_PRINTABLE
    )


def test_cp1252_printable_does_not_encode_as_ascii_or_latin1() -> None:
    with pytest.raises(ValueError):
        codecs.encode(CP1252_PRINTABLE, "ASCII")
    with pytest.raises(ValueError):
        codecs.encode(CP1252_PRINTABLE, "Latin1")


def test_cp1252_printable_does_not_include_control_characters() -> None:
    for c in CP1252_PRINTABLE:
        assert unicodedata.category(c)[0] != "C"


@st.composite
def characters_and_valid_exclusions(draw: Callable[[Any], Any]) -> Tuple[str, str]:
    characters = draw(st.lists(st.characters(), min_size=1).map(lambda l: "".join(l)))
    exclusions = draw(st.lists(st.sampled_from(characters)).map(lambda l: "".join(l)))

    # The resulting set can not be empty.
    assume(set(characters) - set(exclusions))

    return (characters, exclusions)


@st.composite
def characters_and_invalid_exclusions(draw: Callable[[Any], Any]) -> Tuple[str, str]:
    characters = draw(st.lists(st.characters(), min_size=1).map(lambda l: "".join(l)))
    exclusions = draw(st.lists(st.characters(), min_size=1).map(lambda l: "".join(l)))

    # The resulting set can not be empty.
    assume(set(characters) - set(exclusions))

    # There should be exclusions which are not part of the original character set.
    assume(set(exclusions) - set(characters))

    return (characters, exclusions)


@given(characters_and_valid_exclusions())
def test_regex_character_class(characters_exclusions: Tuple[str, str]) -> None:
    characters, exclusions = characters_exclusions

    re = regex.compile(f"[{regex_character_class(characters, exclusions)}]*")

    # A string of all characters which should be matched by the regex.
    characters_excluded = "".join(filter(lambda c: c not in exclusions, characters))
    assert regex.fullmatch(re, characters_excluded)

    # If there are exclusions, the regex should not match the original characters.
    if characters_excluded != characters:
        assert not regex.fullmatch(re, characters)


@given(characters_and_invalid_exclusions())
def test_regex_character_class_fails_given_invalid_exclusions(
    characters_exclusions: Tuple[str, str]
) -> None:
    characters, exclusions = characters_exclusions

    with pytest.raises(ValueError):
        regex_character_class(characters, exclusions)


def test_regex_character_class_fails_given_empty_class() -> None:
    with pytest.raises(ValueError):
        regex_character_class("")

    with pytest.raises(ValueError):
        regex_character_class("abc", "abc")
