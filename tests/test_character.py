from pathlib import Path
from typing import Callable
from typing import Generator
from typing import MutableMapping
from typing import Union

import pytest

from swtor_settings_updater.character import CharacterMetadata
from swtor_settings_updater.character import update_all
from swtor_settings_updater.character import update_path


SETTINGS_PATH_A = Path("swtor/settings/he4242_Kai Zykken_PlayerGUIState.ini")
SETTINGS_PATH_B = Path("publictest/settings/HE4343_Plagueis_PlayerGUIState.ini")
OTHER_PATH = Path("swtor/settings/Other.ini")

# fmt: off

SETTINGS_FILE_A_CONTENT_BEFORE = (
    b"[Settings]\n"
    b"Show_Chat_Timestamp = false\n"
    b"Test = \x80\xe4\xf6\n"
)

SETTINGS_FILE_A_CONTENT_AFTER = (
    b"[Settings]\r\n"
    b"Show_Chat_Timestamp = false\r\n"
    b"Test = \xf6\xe4\x80\r\n"
    b"GUI_QuickslotLockState = true\r\n"
    b"gui_showcooldowntext = true\r\n"
    b"\r\n"
)


SETTINGS_FILE_B_CONTENT_BEFORE = (
    b"# Comment\r\n"
    b"\r\n"
    b"[Settings]\r\n"
    b"\r\n"
    b"GUI_ShowCooldownText = false\r\n"
    b"\r\n"
    b"Test = \x80\xe4\xf6\r\n"
    b"\r\n"
    b"[Another Section]\r\n"
    b"\r\n"
    b"General = Kenobi\r\n"
    b"\r\n"
    b"\r\n"
)

SETTINGS_FILE_B_CONTENT_AFTER = (
    b"[Settings]\r\n"
    b"GUI_ShowCooldownText = true\r\n"
    b"Test = \xf6\xe4\x80\r\n"
    b"GUI_QuickslotLockState = true\r\n"
    b"\r\n"
    b"[Another Section]\r\n"
    b"General = Kenobi\r\n"
    b"\r\n"
)


OTHER_FILE_CONTENT = (
    b"[Hello There]\n"
    b"General = Kenobi"
)

# fmt: on


# For testing both str and Path inputs.
PathFunction = Callable[[Union[str, Path]], Union[str, Path]]


def update_settings(_character: CharacterMetadata, s: MutableMapping[str, str]) -> None:
    s["GUI_QuickslotLockState"] = "true"
    s["gui_showcooldowntext"] = "true"
    s["tEST"] = "öä€"


@pytest.fixture()
def settings_dir(tmp_path: Path) -> Generator[Path, None, None]:
    expected_paths = set()

    for environment in [tmp_path / "swtor", tmp_path / "publictest"]:
        for d in [environment, environment / "settings"]:
            d.mkdir()
            expected_paths.add(d)

    settings_file_a = tmp_path / SETTINGS_PATH_A
    settings_file_b = tmp_path / SETTINGS_PATH_B
    other_file = tmp_path / OTHER_PATH

    settings_file_a.write_bytes(SETTINGS_FILE_A_CONTENT_BEFORE)
    settings_file_b.write_bytes(SETTINGS_FILE_B_CONTENT_BEFORE)
    other_file.write_bytes(OTHER_FILE_CONTENT)

    expected_paths.add(settings_file_a)
    expected_paths.add(settings_file_b)
    expected_paths.add(other_file)

    yield tmp_path

    # The code should not leave extra files behind (or delete existing files
    # for that matter).
    assert (
        set(tmp_path.rglob("*")) == expected_paths
    ), "A file was added or removed in the settings directory"

    assert (
        other_file.read_bytes() == OTHER_FILE_CONTENT
    ), "An unrelated file was modified in the settings directory"


@pytest.mark.parametrize("path_fun", [str, Path])
def test_character_update_path_parses_filename(
    path_fun: PathFunction, settings_dir: Path
) -> None:
    settings_filepath = settings_dir / SETTINGS_PATH_A

    called = False

    def check_metadata(
        character: CharacterMetadata, _s: MutableMapping[str, str]
    ) -> None:
        nonlocal called
        called = True
        assert character.environment == "swtor"
        assert character.server_id == "he4242"
        assert character.name == "Kai Zykken"

    update_path(path_fun(settings_filepath), check_metadata)

    assert called


@pytest.mark.parametrize("path_fun", [str, Path])
def test_character_update_path_fails_to_parse_incorrect_filename(
    path_fun: PathFunction, settings_dir: Path
) -> None:
    other_filepath = settings_dir / OTHER_PATH

    called = False

    def callback(character: CharacterMetadata, _s: MutableMapping[str, str]) -> None:
        nonlocal called
        called = True

    with pytest.raises(ValueError):
        update_path(path_fun(other_filepath), callback)

    assert not called


@pytest.mark.parametrize("path_fun", [str, Path])
def test_character_update_path_updates_settings(
    path_fun: PathFunction, settings_dir: Path
) -> None:
    settings_filepath_a = settings_dir / SETTINGS_PATH_A
    settings_filepath_b = settings_dir / SETTINGS_PATH_B

    update_path(path_fun(settings_filepath_a), update_settings)

    assert (
        settings_filepath_a.read_bytes() == SETTINGS_FILE_A_CONTENT_AFTER
    ), "The settings file was not modified in the expected way"

    assert (
        settings_filepath_b.read_bytes() == SETTINGS_FILE_B_CONTENT_BEFORE
    ), "Another settings file was modified unexpectedly"


@pytest.mark.parametrize("path_fun", [str, Path])
def test_character_update_path_does_not_modify_settings_given_invalid_characters(
    path_fun: PathFunction, settings_dir: Path,
) -> None:
    """The settings files are encoded in CP1252."""
    settings_filepath = settings_dir / SETTINGS_PATH_A

    def update_settings_invalid(
        _character: CharacterMetadata, s: MutableMapping[str, str]
    ) -> None:
        s["Invalid"] = "√☃🤦"

    with pytest.raises(UnicodeEncodeError):
        update_path(path_fun(settings_filepath), update_settings_invalid)

    # The file must be unchanged.
    assert settings_filepath.read_bytes() == SETTINGS_FILE_A_CONTENT_BEFORE


@pytest.mark.parametrize("path_fun", [str, Path])
def test_character_update_all_updates_settings(
    path_fun: PathFunction, settings_dir: Path
) -> None:
    settings_filepath_a = settings_dir / SETTINGS_PATH_A
    settings_filepath_b = settings_dir / SETTINGS_PATH_B

    update_all(path_fun(settings_dir), update_settings)

    assert settings_filepath_a.read_bytes() == SETTINGS_FILE_A_CONTENT_AFTER
    assert settings_filepath_b.read_bytes() == SETTINGS_FILE_B_CONTENT_AFTER
