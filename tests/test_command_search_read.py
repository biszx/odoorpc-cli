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
