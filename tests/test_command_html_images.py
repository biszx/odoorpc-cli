import base64
import json

import pytest
from click.testing import CliRunner
from odoorpc_cli.cli import odoo
from odoorpc_cli.settings import Settings

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


@pytest.fixture
def runner():
    return CliRunner()


def create_task(runner, description):
    res = runner.invoke(
        odoo,
        [
            "create",
            "project.task",
            "--values",
            json.dumps([{"name": "ImageTask", "description": description}]),
        ],
    )
    assert res.exit_code == 0, res.output
    return json.loads(res.output)["ids"][0]


def read_task(runner, task_id, *extra):
    res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "project.task",
            "--domain",
            json.dumps([["id", "=", task_id]]),
            "--fields",
            "name,description",
            *extra,
        ],
    )
    assert res.exit_code == 0, res.output
    return json.loads(res.output)[0]


def test_search_read_replaces_html_images_with_file_paths(runner, cache_dir):
    task_id = create_task(runner, DATA_URI_HTML)

    record = read_task(runner, task_id)

    assert f"file://{cache_dir}" in record["description"]
    assert PNG_B64 not in record["description"]
    assert len(list(cache_dir.iterdir())) == 1


def test_search_read_raw_keeps_base64(runner):
    task_id = create_task(runner, DATA_URI_HTML)

    record = read_task(runner, task_id, "--raw")

    assert PNG_B64 in record["description"]
    assert "file://" not in record["description"]


def test_create_inlines_file_path_into_data_uri(runner, tmp_path):
    image = tmp_path / "shot.png"
    image.write_bytes(PNG)
    description = f'<p><img src="file://{image}"></p>'

    task_id = create_task(runner, description)
    record = read_task(runner, task_id, "--raw")

    assert f'src="data:image/png;base64,{PNG_B64}"' in record["description"]
    assert "file://" not in record["description"]


def test_create_fails_loudly_when_image_file_is_missing(runner):
    res = runner.invoke(
        odoo,
        [
            "create",
            "project.task",
            "--values",
            json.dumps(
                [{"name": "x", "description": '<img src="file:///nope/missing.png">'}]
            ),
        ],
    )

    assert res.exit_code != 0
    assert "missing.png" in res.output


def test_write_inlines_file_path_into_data_uri(runner, tmp_path):
    task_id = create_task(runner, "<p>plain</p>")
    image = tmp_path / "shot.png"
    image.write_bytes(PNG)

    res = runner.invoke(
        odoo,
        [
            "write",
            "project.task",
            "--ids",
            str(task_id),
            "--value",
            json.dumps({"description": f'<img src="file://{image}">'}),
        ],
    )
    assert res.exit_code == 0, res.output
    record = read_task(runner, task_id, "--raw")

    assert f"data:image/png;base64,{PNG_B64}" in record["description"]
