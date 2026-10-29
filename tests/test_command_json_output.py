import json

import pytest
from click.testing import CliRunner
from odoorpc_cli.cli import odoo


@pytest.fixture
def runner():
    return CliRunner()


def test_search_read_is_minified_by_default(runner):
    res = runner.invoke(
        odoo, ["search", "read", "res.partner", "--domain", "[]", "--fields", "name"]
    )

    assert res.exit_code == 0
    output = res.output.strip()
    assert "\n" not in output
    assert ", " not in output
    assert json.loads(output)


def test_pretty_flag_on_the_group_indents_output(runner):
    res = runner.invoke(
        odoo,
        [
            "--pretty",
            "search",
            "read",
            "res.partner",
            "--domain",
            "[]",
            "--fields",
            "name",
        ],
    )

    assert res.exit_code == 0
    assert res.output.splitlines()[0] == "["
    assert json.loads(res.output)


def test_model_field_is_minified_by_default(runner):
    res = runner.invoke(odoo, ["model", "field", "res.partner"])

    assert res.exit_code == 0
    assert "\n" not in res.output.strip()
    assert json.loads(res.output)


def test_pretty_flag_applies_to_model_field(runner):
    res = runner.invoke(odoo, ["--pretty", "model", "field", "res.partner"])

    assert res.exit_code == 0
    assert len(res.output.splitlines()) > 1
    assert json.loads(res.output)


def test_count_is_minified_by_default(runner):
    res = runner.invoke(odoo, ["search", "count", "res.partner"])

    assert res.exit_code == 0
    assert "\n" not in res.output.strip()
    assert "count" in json.loads(res.output)
