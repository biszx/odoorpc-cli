import json

from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_call_method_search_read():
    # autouse fixture in tests/conftest.py sets up config and client mocking
    runner = CliRunner()
    # call ir.model.search_read to get at least one model entry
    res = runner.invoke(
        odoo,
        [
            "call-method",
            "ir.model",
            "--method",
            "search_read",
            "--args",
            "[]",
            "--kwargs",
            json.dumps({"fields": ["model"], "limit": 1}),
        ],
    )
    assert res.exit_code == 0
    assert "model" in res.output
