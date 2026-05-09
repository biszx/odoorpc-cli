import json
import uuid

from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_create_and_cleanup():
    # autouse fixture in tests/conftest.py configures a temp Settings and
    # patches OdooClient when the local server is unreachable. Rely on that.
    runner = CliRunner()
    unique = f"TestCreate-{uuid.uuid4().hex[:6]}"
    values = json.dumps([{"name": unique}])
    res = runner.invoke(odoo, ["create", "res.partner", "--values", values])
    assert res.exit_code == 0
    assert '"ids"' in res.output
    out = json.loads(res.output)
    ids = out.get("ids") or []
    assert isinstance(ids, list) and len(ids) >= 1

    # cleanup created records via CLI so the patched client is used
    runner.invoke(odoo, ["unlink", "res.partner", "--ids", ",".join(map(str, ids))])
