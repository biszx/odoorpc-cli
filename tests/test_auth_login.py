import odoorpc_cli.cli as cli_mod
from click.testing import CliRunner
from odoorpc_cli.commands.auth import login as login_mod


def test_auth_login_invokes_save_and_client(monkeypatch, tmp_path):
    runner = CliRunner()

    # Patch the odoorpc_client used by the login module to avoid network calls
    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(login_mod, "odoorpc_client", DummyClient)

    res = runner.invoke(
        cli_mod.odoo,
        [
            "auth",
            "login",
            "--host",
            "http://x",
            "--db",
            "d",
            "--username",
            "u",
            "--password",
            "p",
        ],
    )

    assert res.exit_code == 0
    assert "Login successful!" in res.output
