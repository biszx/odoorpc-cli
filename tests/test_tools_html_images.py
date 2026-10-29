import base64
import hashlib
import os
import time

import pytest
from odoorpc_cli.settings import Settings
from odoorpc_cli.tools import html_images

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
PNG_B64 = base64.b64encode(PNG).decode()
DATA_URI_HTML = f'<p><img class="img-fluid" src="data:image/png;base64,{PNG_B64}"></p>'


@pytest.fixture(autouse=True)
def cache_dir(tmp_path, monkeypatch):
    path = tmp_path / "images"
    monkeypatch.setattr(Settings, "IMAGE_DIR", str(path))
    return path


def test_externalize_replaces_data_uri_with_file_path(cache_dir):
    out = html_images.externalize_images(DATA_URI_HTML)

    expected = cache_dir / f"{hashlib.sha1(PNG).hexdigest()}.png"
    assert f'src="file://{expected}"' in out
    assert expected.read_bytes() == PNG
    assert PNG_B64 not in out


def test_externalize_leaves_html_without_images_unchanged():
    html = "<p>no images here</p>"
    assert html_images.externalize_images(html) == html


def test_externalize_dedupes_identical_images(cache_dir):
    html_images.externalize_images(DATA_URI_HTML)
    html_images.externalize_images(DATA_URI_HTML)

    assert len(list(cache_dir.iterdir())) == 1


def test_inline_restores_data_uri_from_file_path(cache_dir):
    external = html_images.externalize_images(DATA_URI_HTML)

    back = html_images.inline_images(external)

    assert f"data:image/png;base64,{PNG_B64}" in back
    assert "file://" not in back


def test_inline_raises_when_file_is_missing():
    with pytest.raises(FileNotFoundError):
        html_images.inline_images('<p><img src="file:///nonexistent/missing.png"></p>')


def test_inline_leaves_html_without_file_uri_unchanged():
    html = '<p><img src="https://example.com/a.png"></p>'
    assert html_images.inline_images(html) == html


def test_prune_cache_removes_only_old_files(cache_dir):
    cache_dir.mkdir(parents=True)
    stale = cache_dir / "stale.png"
    fresh = cache_dir / "fresh.png"
    stale.write_bytes(b"stale")
    fresh.write_bytes(b"fresh")
    old = time.time() - 30 * 86400
    os.utime(stale, (old, old))

    removed = html_images.prune_cache()

    assert removed == 1
    assert not stale.exists()
    assert fresh.exists()


def test_is_html_field_checks_declared_type():
    meta = {"description": {"type": "html"}, "name": {"type": "char"}}

    assert html_images.is_html_field(meta, "description") is True
    assert html_images.is_html_field(meta, "name") is False
    assert html_images.is_html_field(meta, "absent") is False
