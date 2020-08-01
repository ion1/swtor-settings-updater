from hypothesis import given
import hypothesis.strategies as st
import regex

from swtor_settings_updater.util.swtor_case import swtor_lower, swtor_upper


@given(st.text())
def test_swtor_lower(string: str) -> None:
    lowered = swtor_lower(string)
    assert len(lowered) == len(string)
    assert swtor_lower(lowered) == lowered
    assert swtor_lower(swtor_upper(string)) == lowered
    assert not regex.match("[A-Z]", lowered)


@given(st.text())
def test_swtor_upper(string: str) -> None:
    uppered = swtor_upper(string)
    assert len(uppered) == len(string)
    assert swtor_upper(uppered) == uppered
    assert swtor_upper(swtor_lower(string)) == uppered
    assert not regex.match("[a-z]", uppered)
