import configparser

from swtor_settings_updater.util.option_transformer import OptionTransformer


def test_option_transformer_preserves_case() -> None:
    option_transformer = OptionTransformer()

    parser0 = configparser.ConfigParser()
    option_transformer.install(parser0)
    parser0["Foo"] = {"hElLo": "there"}
    parser0["Foo"] = {"hello": "there"}

    assert list(parser0["Foo"].keys()) == ["hElLo"]

    parser1 = configparser.ConfigParser()
    option_transformer.install(parser1)
    parser1["Foo"] = {"HELLO": "there"}

    assert list(parser1["Foo"].keys()) == ["hElLo"]
