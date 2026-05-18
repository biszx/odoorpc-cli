from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_search_read_basic():
    runner = CliRunner()
    res = runner.invoke(odoo, ["search", "read", "res.partner"])
    assert res.exit_code == 0
    assert '"id"' in res.output


def test_search_read_with_options():
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--domain",
            "[]",
            "--fields",
            "name",
            "--limit",
            "1",
        ],
    )
    assert res.exit_code == 0
    assert '"name"' in res.output


def test_search_read_with_order_asc():
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--order",
            "name asc",
        ],
    )
    assert res.exit_code == 0
    assert '"id"' in res.output


def test_search_read_with_order_desc():
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--order",
            "id desc",
        ],
    )
    assert res.exit_code == 0
    assert '"id"' in res.output


def test_search_read_with_order_field_only():
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--order",
            "name",
        ],
    )
    assert res.exit_code == 0
    assert '"id"' in res.output


def test_search_read_with_invalid_direction():
    """Test that invalid direction still works but doesn't break the command"""
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--order",
            "name invalid",
        ],
    )
    assert res.exit_code == 0
    assert '"id"' in res.output
    # The command should work even with invalid direction
