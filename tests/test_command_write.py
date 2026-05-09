import json

from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_write_updates_record():
    # Use autouse fixture in tests/conftest.py for config and client patching
    runner = CliRunner()
    # create the record via the CLI so the same (possibly patched) client
    # instance/store is used by subsequent commands
    create_res = runner.invoke(
        odoo,
        ["create", "res.partner", "--values", json.dumps([{"name": "WriteTest"}])],
    )
    assert create_res.exit_code == 0
    created = json.loads(create_res.output)
    ids = created.get("ids")
    assert ids
    rid = ids[0]
    res = runner.invoke(
        odoo,
        [
            "write",
            "res.partner",
            "--id",
            str(rid),
            "--value",
            json.dumps({"name": "UpdatedName"}),
        ],
    )
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out.get("success") is True

    # verify the change by reading the record back via the CLI
    domain = json.dumps([["id", "=", rid]])
    read_res = runner.invoke(
        odoo,
        [
            "search",
            "read",
            "res.partner",
            "--domain",
            domain,
            "--fields",
            "id,name",
            "--limit",
            "1",
        ],
    )
    assert read_res.exit_code == 0
    recs = json.loads(read_res.output)
    assert recs, "expected to find the updated record"
    assert recs[0].get("name") == "UpdatedName"

    # cleanup via CLI
    runner.invoke(odoo, ["unlink", "res.partner", "--ids", str(rid)])


def test_write_with_domain():
    runner = CliRunner()
    # create a record via CLI
    create_res = runner.invoke(
        odoo,
        ["create", "res.partner", "--values", json.dumps([{"name": "WDomain"}])],
    )
    assert create_res.exit_code == 0
    created = json.loads(create_res.output)
    ids = created.get("ids")
    assert ids
    rid = ids[0]

    domain = json.dumps([["id", "=", rid]])
    res = runner.invoke(
        odoo,
        [
            "write",
            "res.partner",
            "--domain",
            domain,
            "--value",
            json.dumps({"name": "DomainUpdated"}),
        ],
    )
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out.get("success") is True


def test_write_no_selection():
    runner = CliRunner()
    res = runner.invoke(
        odoo,
        ["write", "res.partner", "--value", json.dumps({"name": "X"})],
    )
    assert res.exit_code == 0
    out = json.loads(res.output)
    assert out == {"success": False, "ids": []}
