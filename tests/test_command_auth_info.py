from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_info_returns_user():
    # autouse fixture in tests/conftest.py configures temp Settings and client
    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "info"])
    assert res.exit_code == 0
    # should return a JSON object describing the current user
    assert "id" in res.output or "login" in res.output
