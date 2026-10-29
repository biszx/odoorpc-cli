"""Move embedded base64 images in html fields out to files, and back on write.

Reading a record whose html field carries a pasted screenshot returns megabytes of
base64; writing one means producing that base64. Both are swapped for a plain file
path on disk so the value stays workable in a terminal.
"""

import base64
import hashlib
import os
import re
import time

from odoorpc_cli.settings import Settings

DATA_URI_RE = re.compile(r'src="data:(image/(?:png|jpeg|jpg|gif|webp|bmp|svg\+xml));base64,([A-Za-z0-9+/=\s]+)"')
FILE_URI_RE = re.compile(r'src="file://([^"]+)"')

EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/svg+xml": ".svg",
}
MIME_TYPES = {ext: mime for mime, ext in EXTENSIONS.items()}


def is_html_field(field_meta: dict, name: str) -> bool:
    """True when `name` is declared as an html field in a `fields_get()` result."""
    return (field_meta.get(name) or {}).get("type") == "html"


def externalize_images(html: str) -> str:
    """Write every embedded base64 image to the cache and point its src at the file."""
    cache = Settings.IMAGE_DIR
    os.makedirs(cache, exist_ok=True)

    def replace(match):
        mime, payload = match.group(1), re.sub(r"\s+", "", match.group(2))
        blob = base64.b64decode(payload)
        path = os.path.join(cache, hashlib.sha1(blob).hexdigest() + EXTENSIONS[mime])
        if not os.path.exists(path):
            with open(path, "wb") as fh:
                fh.write(blob)
        return f'src="file://{path}"'

    return DATA_URI_RE.sub(replace, html)


def inline_images(html: str) -> str:
    """Replace every `file://` image src with the base64 data URI of that file."""

    def replace(match):
        path = match.group(1)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"image not found: {path}")
        mime = MIME_TYPES.get(os.path.splitext(path)[1].lower(), "image/png")
        with open(path, "rb") as fh:
            payload = base64.b64encode(fh.read()).decode()
        return f'src="data:{mime};base64,{payload}"'

    return FILE_URI_RE.sub(replace, html)


def prune_cache() -> int:
    """Delete cached images older than Settings.IMAGE_MAX_AGE_DAYS; return how many."""
    cache = Settings.IMAGE_DIR
    if not os.path.isdir(cache):
        return 0
    cutoff = time.time() - Settings.IMAGE_MAX_AGE_DAYS * 86400
    removed = 0
    for entry in os.scandir(cache):
        if entry.is_file() and entry.stat().st_mtime < cutoff:
            os.remove(entry.path)
            removed += 1
    return removed
