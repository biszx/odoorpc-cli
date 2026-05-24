import json
import os
import time
import urllib.error
import pytest
from odoorpc_cli import __version__
from odoorpc_cli.tools.version_check import (
    CACHE_FILE,
    check_for_updates,
    get_latest_version,
    parse_version,
)


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


def test_parse_version():
    assert parse_version("1.2.0") == (1, 2, 0)
    assert parse_version("v1.2.0") == (1, 2, 0)
    assert parse_version("  v2.3.4  ") == (2, 3, 4)
    assert parse_version("1.2b3") == (1, 23)
    assert parse_version("1.foo.2") == (1, 0, 2)


def test_get_latest_version_success(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.data = json.dumps({"info": {"version": "9.9.9"}}).encode("utf-8")

        def read(self):
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda req, timeout=None: DummyResponse(),
    )

    assert get_latest_version() == "9.9.9"


def test_get_latest_version_failure(monkeypatch):
    def mock_urlopen(req, timeout=None):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    assert get_latest_version() is None


def test_check_for_updates_no_cache_no_update(monkeypatch):
    # Remove cache file if it exists
    if os.path.exists(CACHE_FILE):
        try:
            os.remove(CACHE_FILE)
        except Exception:
            pass

    # Mock get_latest_version to return the current version (no update available)
    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        lambda: __version__,
    )

    is_avail, latest = check_for_updates(force=True)
    assert not is_avail
    assert latest is None


def test_check_for_updates_cache_not_expired(monkeypatch):
    # Setup cache file with a valid version but old check time (within 24h)
    # So it won't fetch from PyPI again
    now = time.time()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_check": now - 1000, "latest_version": "99.9.9"}, f)

    called = False

    def mock_get_latest():
        nonlocal called
        called = True
        return "100.0.0"

    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        mock_get_latest,
    )

    # force=False, cache is young -> should use cache and find 99.9.9 is newer
    is_avail, latest = check_for_updates(force=False)
    assert not called
    assert is_avail
    assert latest == "99.9.9"


def test_check_for_updates_cache_expired(monkeypatch):
    # Setup cache file with check time older than 24h
    now = time.time()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_check": now - 90000, "latest_version": "0.1.0"}, f)

    called = False

    def mock_get_latest():
        nonlocal called
        called = True
        return "9.9.9"

    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        mock_get_latest,
    )

    # force=False, cache is old -> should trigger fetch
    is_avail, latest = check_for_updates(force=False)
    assert called
    assert is_avail
    assert latest == "9.9.9"


def test_check_for_updates_write_cache_failure(monkeypatch):
    # Force write cache to raise exception
    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        lambda: "9.9.9",
    )

    # Monkeypatch open to raise error when writing to CACHE_FILE
    original_open = open

    def mock_open(file, *args, **kwargs):
        if file == CACHE_FILE and "w" in args[0]:
            raise PermissionError("Write forbidden")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    # Should not crash, but complete successfully
    is_avail, latest = check_for_updates(force=True)
    assert is_avail
    assert latest == "9.9.9"


def test_check_for_updates_read_cache_failure(monkeypatch):
    # Setup a corrupt cache file
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write("{invalid json}")

    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        lambda: "9.9.9",
    )

    # Should gracefully handle bad JSON and fetch
    is_avail, latest = check_for_updates(force=False)
    assert is_avail
    assert latest == "9.9.9"


def test_check_for_updates_offline_failure_caches_last_check(monkeypatch):
    # Setup cache file with check time older than 24h and some cached version
    now = time.time()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_check": now - 90000, "latest_version": "9.9.9"}, f)

    # Mock get_latest_version to return None (indicating offline/timeout)
    monkeypatch.setattr(
        "odoorpc_cli.tools.version_check.get_latest_version",
        lambda: None,
    )

    # force=False -> should attempt fetch, fail, and save current time to last_check
    is_avail, latest = check_for_updates(force=False)
    # The cache should still contain the old cached version 9.9.9, so we still warn if it was newer
    assert is_avail
    assert latest == "9.9.9"

    # Verify that cache file was updated with a fresh last_check time
    assert os.path.exists(CACHE_FILE)
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
        assert cache["last_check"] >= now
        assert cache["latest_version"] == "9.9.9"

