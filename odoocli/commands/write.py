import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("write")
@click.argument("model")
@click.option("--id", "ids", required=True, help="Comma-separated id(s) to update")
@click.option("--value", required=True, help="Values as JSON object")
def write(model: str, ids: str, value: str) -> None:
    """Update records by IDs"""
    ensure_config_exists()
    client = OdooClient.from_config()
    vals = json.loads(value)
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    ok = client.write(model, id_list, vals)
    click.echo(json.dumps({"success": bool(ok)}))
