import json
import os
import time
import urllib.request

from odoorpc_cli import __version__
from odoorpc_cli.settings import Settings


def parse_version(v_str: str) -> tuple[int, ...]:
    """Parse a semantic version string into a tuple of integers for comparison.

    Any non-digit parts are ignored or mapped to 0.
    """
    parts = []
    for part in v_str.split("."):
        digits = "".join(c for c in part if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def get_latest_version() -> str | None:
    """Fetch the latest version from PyPI with a timeout."""
    url = "https://pypi.org/pypi/odoorpc-cli/json"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": f"odoorpc-cli/{__version__}"}
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["info"]["version"]
    except Exception:
        return None


def check_for_updates(force: bool = False) -> tuple[bool, str | None]:
    """Check if a new version is available.

    Returns (is_available, latest_version) if we checked and found a new version,
    or (False, None) otherwise.
    """
    Settings.ensure_dir()
    now = time.time()

    cached_version = None
    last_check = 0.0

    if os.path.exists(Settings.UPDATE_CHECK_PATH):
        try:
            with open(Settings.UPDATE_CHECK_PATH, encoding="utf-8") as f:
                cache = json.load(f)
                cached_version = cache.get("latest_version")
                last_check = cache.get("last_check", 0.0)
        except Exception:
            pass

    # Fetch from PyPI if forced or if the cache is older than the interval
    if force or (now - last_check > Settings.UPDATE_CHECK_INTERVAL):
        latest = get_latest_version()
        if latest:
            cached_version = latest

        last_check = now
        try:
            with open(Settings.UPDATE_CHECK_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {"last_check": last_check, "latest_version": cached_version},
                    f,
                )
        except Exception:
            pass

    if cached_version:
        current_parsed = parse_version(__version__)
        latest_parsed = parse_version(cached_version)
        if latest_parsed > current_parsed:
            return True, cached_version

    return False, None
