import pytest
from odoorpc_cli.tools.click_types import JSON


def test_json_invalid_expected_raises():
    with pytest.raises(ValueError):
        JSON(expected="bad")


def test_json_convert_with_object_returns_same():
    j = JSON(expected="list")
    obj = [1, 2, 3]
    assert j.convert(obj, None, None) == obj


def test_json_convert_with_string_parses_and_validates():
    j = JSON(expected="list")
    out = j.convert("[1,2]", None, None)
    assert isinstance(out, list)


def test_json_repr():
    j = JSON(expected=None)
    assert "JSON(expected=None)" in repr(j)


def test_json_convert_type_mismatch_raises():
    import click

    j = JSON(expected="list")
    with pytest.raises(click.BadParameter):
        j.convert({"a": 1}, None, None)


def test_json_convert_dict_expected_raises():
    import click

    j = JSON(expected="dict")
    with pytest.raises(click.BadParameter):
        j.convert([1, 2], None, None)
