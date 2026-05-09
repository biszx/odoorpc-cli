import json

from click.testing import CliRunner
from odoorpc_cli.cli import odoo
from odoorpc_cli.tools.odoo_client import OdooClient


def test_unlink_existing_record():
    client = OdooClient.from_config()
    # create a record to delete
    ids = client.create("res.partner", [{"name": "ToDelete"}])
    assert isinstance(ids, list) and ids

    runner = CliRunner()
    res = runner.invoke(
        odoo, ["unlink", "res.partner", "--ids", ",".join(map(str, ids))]
    )
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out.get("success") is True

    # ensure record no longer counted
    count = client.search_count("res.partner", [["id", "in", ids]])
    assert count == 0
