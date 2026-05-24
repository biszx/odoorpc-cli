import os

import pytest
from click.testing import CliRunner
from odoorpc_cli.cli import odoo
from odoorpc_cli.settings import Settings


def test_auth_logout_when_authenticated(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg_auth"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(cfg_dir / "machine.key"))

    # First, let's make sure it is authenticated by saving a config
    Settings.save(
        host="http://localhost:8069", db="dev", username="admin", password="admin"
    )
    assert os.path.isfile(Settings.CONFIG_PATH)

    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "logout"])
    assert res.exit_code == 0
    assert "Successfully logged out." in res.output
    with pytest.raises(RuntimeError) as exc_info:
        Settings.load()  # should raise since config is cleared
    assert (
        str(exc_info.value)
        == "Not authenticated — run 'odoo auth login' to authenticate"
    )


def test_auth_logout_when_not_authenticated(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg_unauth"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(cfg_dir / "machine.key"))

    # config file does not exist
    assert not os.path.exists(Settings.CONFIG_PATH)

    runner = CliRunner()
    res = runner.invoke(odoo, ["auth", "logout"])
    assert res.exit_code == 0
    assert "Not authenticated — run 'odoo auth login' to authenticate" in res.output
