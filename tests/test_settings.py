import json
import os

import pytest
from odoorpc_cli.settings import Settings


def test_encrypt_decrypt_roundtrip(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg_roundtrip"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(cfg_dir / "machine.key"))

    plain = "s3cr3t!"
    token = Settings.encrypt_password(plain)
    assert Settings.decrypt_password(token) == plain


def test_save_and_load_config(tmp_path, monkeypatch):
    # Redirect config directory to a temporary path to avoid touching the real home
    cfg_dir = tmp_path / ".odoo"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(cfg_dir / "machine.key"))

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


def test_get_or_create_key_writes_and_reads(tmp_path, monkeypatch):
    # Use a temp directory for the key file to avoid touching the real home
    cfg_dir = tmp_path / "cfg"
    key_path = cfg_dir / "machine.key"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(key_path))

    key1 = Settings._get_or_create_key()
    assert isinstance(key1, (bytes, bytearray))
    # Calling again should read the same key
    key2 = Settings._get_or_create_key()
    assert key1 == key2
    assert os.path.isfile(str(key_path))


def test_get_or_create_key_cleans_temp_on_replace_error(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg2"
    key_path = cfg_dir / "machine.key"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(key_path))

    # Simulate os.replace failing so the temp file must be cleaned up
    original_replace = os.replace

    def bad_replace(src, dst):
        raise OSError("replace-failed")

    monkeypatch.setattr(os, "replace", bad_replace)

    temp_path = str(key_path) + ".tmp"
    with pytest.raises(OSError):
        Settings._get_or_create_key()

    # temp file should not be left behind
    assert not os.path.exists(temp_path)

    # restore original behavior for cleanliness
    monkeypatch.setattr(os, "replace", original_replace)


def test_get_or_create_key_swallow_remove_exception(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg3"
    key_path = cfg_dir / "machine.key"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(key_path))

    # Make os.replace copy the temp file (leave temp file behind), then make os.remove raise
    import shutil

    monkeypatch.setattr(os, "replace", lambda src, dst: shutil.copyfile(src, dst))

    def bad_remove(p):
        raise OSError("remove-failed")

    monkeypatch.setattr(os, "remove", bad_remove)

    # Should not raise; removal error is swallowed
    Settings._get_or_create_key()


def test_clear_config(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "cfg4"
    monkeypatch.setattr(Settings, "CONFIG_DIR", str(cfg_dir))
    monkeypatch.setattr(Settings, "CONFIG_PATH", str(cfg_dir / "config.json"))
    monkeypatch.setattr(Settings, "KEY_PATH", str(cfg_dir / "machine.key"))

    # When config does not exist, clear should not fail
    assert not os.path.exists(Settings.CONFIG_PATH)
    Settings.clear()

    # When config exists, clear should delete it
    Settings.save("host", "db", "user", "pass")
    assert os.path.isfile(Settings.CONFIG_PATH)
    Settings.clear()
    with open(Settings.CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("host") is None
    assert data.get("db") is None
    assert data.get("username") is None
    assert data.get("password_encrypted") is None
