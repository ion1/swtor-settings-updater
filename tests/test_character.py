import configparser
import pytest

from swtor_settings_updater.character import Character, OptionTransformer


SETTINGS_FILENAME_A = "he4242_Kai Zykken_PlayerGUIState.ini"
SETTINGS_FILENAME_B = "he4343_Plagueis_PlayerGUIState.ini"
OTHER_FILENAME = "Irrelevant.ini"

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
    b"GUI_ShowCooldownText = true\r\n"
    b"\r\n"
)


SETTINGS_FILE_B_CONTENT_BEFORE = (
    b"# Comment\r\n"
    b"\r\n"
    b"[Settings]\r\n"
    b"\r\n"
    b"gui_showcooldowntext = false\r\n"
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


def update_settings(_server_id, _character_name, s):
    s["GUI_QuickslotLockState"] = "true"
    s["GUI_ShowCooldownText"] = "true"
    s["tEST"] = "öä€"


@pytest.fixture()
def settings_dir(tmp_path):
    settings_file_a = tmp_path / SETTINGS_FILENAME_A
    settings_file_b = tmp_path / SETTINGS_FILENAME_B
    other_file = tmp_path / OTHER_FILENAME

    settings_file_a.write_bytes(SETTINGS_FILE_A_CONTENT_BEFORE)
    settings_file_b.write_bytes(SETTINGS_FILE_B_CONTENT_BEFORE)
    other_file.write_bytes(OTHER_FILE_CONTENT)

    yield tmp_path

    # The code should not leave extra files behind (or delete existing files
    # for that matter).
    assert set(map(lambda p: p.name, tmp_path.iterdir())) == set(
        [SETTINGS_FILENAME_A, SETTINGS_FILENAME_B, OTHER_FILENAME]
    ), "A file was added or removed in the settings directory"

    assert (
        other_file.read_bytes() == OTHER_FILE_CONTENT
    ), "An unrelated file was modified in the settings directory"

def test_character_update_path_parses_filename(settings_dir):
    settings_filepath = settings_dir / SETTINGS_FILENAME_A

    called = [False]

    def check_metadata(server_id, character_name, _s):
        called[0] = True
        assert server_id == "he4242"
        assert character_name == "Kai Zykken"

    Character().update_path(settings_filepath, check_metadata)

    assert called[0]


def test_character_update_path_updates_settings(settings_dir):
    settings_filepath_a = settings_dir / SETTINGS_FILENAME_A
    settings_filepath_b = settings_dir / SETTINGS_FILENAME_B

    Character().update_path(str(settings_filepath_a), update_settings)

    assert (
        settings_filepath_a.read_bytes() == SETTINGS_FILE_A_CONTENT_AFTER
    ), "The settings file was not modified in the expected way"

    assert (
        settings_filepath_b.read_bytes() == SETTINGS_FILE_B_CONTENT_BEFORE
    ), "Another settings file was modified unexpectedly"


def test_character_update_path_does_not_modify_settings_given_invalid_characters(
    settings_dir,
):
    """The settings files are encoded in CP1252."""
    settings_filepath = settings_dir / SETTINGS_FILENAME_A

    def update_settings_invalid(_server_id, _character_name, s):
        s["Invalid"] = "√☃🤦"

    with pytest.raises(UnicodeEncodeError):
        Character().update_path(settings_filepath, update_settings_invalid)

    # The file must be unchanged.
    assert settings_filepath.read_bytes() == SETTINGS_FILE_A_CONTENT_BEFORE


def test_character_update_all_updates_settings(settings_dir):
    settings_filepath_a = settings_dir / SETTINGS_FILENAME_A
    settings_filepath_b = settings_dir / SETTINGS_FILENAME_B

    Character().update_all(settings_dir, update_settings)

    assert settings_filepath_a.read_bytes() == SETTINGS_FILE_A_CONTENT_AFTER
    assert settings_filepath_b.read_bytes() == SETTINGS_FILE_B_CONTENT_AFTER


def test_option_transformer_preserves_case():
    option_transformer = OptionTransformer()

    parser0 = configparser.ConfigParser()
    parser0.optionxform = option_transformer.xform
    parser0["Foo"] = {"hElLo": "there"}

    assert list(parser0["Foo"].keys()) == ["hElLo"]

    parser1 = configparser.ConfigParser()
    parser1.optionxform = option_transformer.xform
    parser1["Foo"] = {"HELLO": "bye"}

    assert list(parser1["Foo"].keys()) == ["hElLo"]


def test_option_transformer_does_not_preserve_lower_case():
    option_transformer = OptionTransformer()

    parser0 = configparser.ConfigParser()
    parser0.optionxform = option_transformer.xform
    parser0["Foo"] = {"hello": "there"}

    assert list(parser0["Foo"].keys()) == ["hello"]

    parser1 = configparser.ConfigParser()
    parser1.optionxform = option_transformer.xform
    parser1["Foo"] = {"hElLo": "bye"}

    assert list(parser1["Foo"].keys()) == ["hElLo"]
