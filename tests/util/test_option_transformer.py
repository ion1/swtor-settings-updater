import configparser

from swtor_settings_updater.util.option_transformer import OptionTransformer


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
