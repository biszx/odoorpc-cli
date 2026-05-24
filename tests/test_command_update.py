import sys
from click.testing import CliRunner
from odoorpc_cli import __version__
from odoorpc_cli.commands.update import update


def test_update_command_already_up_to_date(monkeypatch):
    # Retrieve the actual module object to patch
    import odoorpc_cli.commands.update as _unused  # ensure it is imported
    update_mod = sys.modules["odoorpc_cli.commands.update"]

    # Mock check_for_updates on the module to return False (no update available)
    monkeypatch.setattr(
        update_mod,
        "check_for_updates",
        lambda force: (False, None),
    )

    runner = CliRunner()
    res = runner.invoke(update)

    assert res.exit_code == 0
    assert "Checking for updates..." in res.output
    assert f"odoorpc-cli is up to date (version {__version__})." in res.output


def test_update_command_new_version_available(monkeypatch):
    # Retrieve the actual module object to patch
    import odoorpc_cli.commands.update as _unused  # ensure it is imported
    update_mod = sys.modules["odoorpc_cli.commands.update"]

    # Mock check_for_updates on the module to return True (update available to 9.9.9)
    monkeypatch.setattr(
        update_mod,
        "check_for_updates",
        lambda force: (True, "9.9.9"),
    )

    runner = CliRunner()
    res = runner.invoke(update)

    assert res.exit_code == 0
    assert "Checking for updates..." in res.output
    assert "A new version of odoorpc-cli is available: 9.9.9" in res.output
    assert "pip install -U odoorpc-cli" in res.output
    assert "uv tool upgrade odoorpc-cli" in res.output
