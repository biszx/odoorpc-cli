import os
import sys
import pytest
from click.testing import CliRunner
from odoorpc_cli import __version__
from odoorpc_cli.cli import odoo
from odoorpc_cli.tools.version_check import CACHE_FILE


@pytest.fixture(autouse=True)
def clean_cache():
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception:
            pass
    yield
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception:
            pass



def test_cli_shows_update_warning_when_new_version_available(monkeypatch):
    # Retrieve the actual cli module to patch check_for_updates
    import odoorpc_cli.cli as cli_mod
    cli_module = sys.modules["odoorpc_cli.cli"]

    # Mock check_for_updates to return True (9.9.9 available)
    monkeypatch.setattr(
        cli_module,
        "check_for_updates",
        lambda: (True, "9.9.9"),
    )

    # Mock from_config so auth doesn't fail/exit
    monkeypatch.setattr(
        cli_mod.OdooClient,
        "from_config",
        classmethod(lambda _cls: (_ for _ in ()).throw(Exception("no"))),
    )

    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "info"])

    # Output from invoking another subcommand should contain the warning
    assert res.exit_code == 0
    assert "WARNING: A new version of odoorpc-cli is available: 9.9.9" in res.stderr
    assert "To update, run 'odoo update'" in res.stderr


def test_cli_no_warning_when_up_to_date(monkeypatch):
    import odoorpc_cli.cli as cli_mod
    cli_module = sys.modules["odoorpc_cli.cli"]

    # Mock check_for_updates to return False
    monkeypatch.setattr(
        cli_module,
        "check_for_updates",
        lambda: (False, None),
    )

    monkeypatch.setattr(
        cli_mod.OdooClient,
        "from_config",
        classmethod(lambda _cls: (_ for _ in ()).throw(Exception("no"))),
    )

    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "info"])

    assert res.exit_code == 0
    assert "WARNING: A new version of odoorpc-cli is available" not in res.stderr


def test_cli_no_startup_warning_for_update_command_itself(monkeypatch):
    cli_module = sys.modules["odoorpc_cli.cli"]

    # Mock check_for_updates to return True (9.9.9 available)
    called = False

    def mock_check():
        nonlocal called
        called = True
        return (True, "9.9.9")

    monkeypatch.setattr(
        cli_module,
        "check_for_updates",
        mock_check,
    )

    # Mock the update command's own check_for_updates to return False so we don't output upgrade instructions
    import odoorpc_cli.commands.update as update_mod
    update_module = sys.modules["odoorpc_cli.commands.update"]
    monkeypatch.setattr(
        update_module,
        "check_for_updates",
        lambda force: (False, None),
    )

    runner = CliRunner()
    res = runner.invoke(odoo, ["update"])

    assert res.exit_code == 0
    # Startup warning check should NOT have been called (since invoked subcommand is "update")
    assert not called
    assert "WARNING: A new version of odoorpc-cli is available" not in res.stderr


def test_cli_startup_warning_exception_handling(monkeypatch):
    import odoorpc_cli.cli as cli_mod
    cli_module = sys.modules["odoorpc_cli.cli"]

    # Mock check_for_updates to raise an Exception
    def mock_check_raise():
        raise RuntimeError("Network down")

    monkeypatch.setattr(
        cli_module,
        "check_for_updates",
        mock_check_raise,
    )

    monkeypatch.setattr(
        cli_mod.OdooClient,
        "from_config",
        classmethod(lambda _cls: (_ for _ in ()).throw(Exception("no"))),
    )

    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "info"])

    # Should not crash, and execute auth info successfully
    assert res.exit_code == 0
    assert "Not authenticated" in res.output
