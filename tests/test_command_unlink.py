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


def test_unlink_with_domain():
    client = OdooClient.from_config()
    # create a record to delete
    ids = client.create("res.partner", [{"name": "DomainDelete"}])
    assert isinstance(ids, list) and ids
    rid = ids[0]

    runner = CliRunner()
    domain = json.dumps([["id", "=", rid]])
    res = runner.invoke(odoo, ["unlink", "res.partner", "--domain", domain])
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out.get("success") is True


def test_unlink_no_selection():
    runner = CliRunner()
    res = runner.invoke(odoo, ["unlink", "res.partner"])
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out == {"success": False, "ids": []}
