import odoorpc_cli.cli as cli_mod
from click.testing import CliRunner
from odoorpc_cli import __version__
from odoorpc_cli.cli import odoo


def test_version_and_help_options():
    runner = CliRunner()

    # --version should print the package version and exit successfully
    res = runner.invoke(odoo, ["--version"])
    assert res.exit_code == 0
    assert __version__ in res.output

    # -h should display help text and exit successfully
    res2 = runner.invoke(odoo, ["-h"])
    assert res2.exit_code == 0
    assert "Usage" in res2.output


def test_odoo_group_exits_when_not_authenticated(monkeypatch):
    runner = CliRunner()

    # Simulate from_config raising so ctx.obj['odoo'] becomes None
    monkeypatch.setattr(
        cli_mod.OdooClient,
        "from_config",
        classmethod(lambda _cls: (_ for _ in ()).throw(Exception("no"))),
    )

    # Invoke a different subcommand so ctx.invoked_subcommand != 'auth'
    res = runner.invoke(cli_mod.odoo, ["model"])
    assert res.exit_code != 0
    assert "Not authenticated — run 'odoo auth login' to authenticate" in res.output


def test_auth_subcommand_allows_not_authenticated_info(monkeypatch):
    runner = CliRunner()

    # Make from_config raise so ctx.obj['odoo'] is None, but invoking auth should not exit
    monkeypatch.setattr(
        cli_mod.OdooClient,
        "from_config",
        classmethod(lambda _cls: (_ for _ in ()).throw(Exception("no"))),
    )

    res = runner.invoke(cli_mod.odoo, ["auth", "info"])
    assert res.exit_code == 0
    assert "Not authenticated — run 'odoo auth login' to authenticate" in res.output
