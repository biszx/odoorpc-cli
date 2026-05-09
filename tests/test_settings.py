import json

import pytest
from odoorpc_cli.settings import Settings


def test_encrypt_decrypt_roundtrip():
    plain = "s3cr3t!"
    token = Settings.encrypt_password(plain)
    assert Settings.decrypt_password(token) == plain


def test_save_and_load_config(tmp_path, monkeypatch):
    # Redirect config directory to a temporary path to avoid touching the real home
    cfg_dir = tmp_path / ".odoo"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))

    host = "https://example.com"
    db = "demo"
    username = "admin"
    password = "pass123"

    # Save and load should roundtrip the values
    Settings.save(host, db, username, password)
    loaded = Settings.load()
    assert loaded == (host, db, username, password)


def test_load_raises_when_missing(tmp_path, monkeypatch):
    # Point config path to a non-existent file
    dirp = tmp_path / "nodir"
    Settings.CONFIG_DIR = str(dirp)
    Settings.CONFIG_PATH = str(dirp / "config.json")

    with pytest.raises(RuntimeError):
        Settings.load()


def test_load_raises_when_token_missing(tmp_path):
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    Settings.CONFIG_DIR = str(cfg_dir)
    Settings.CONFIG_PATH = str(cfg_dir / "config.json")

    with open(Settings.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"host": "h", "db": "d", "username": "u"}, f)

    with pytest.raises(RuntimeError):
        Settings.load()
