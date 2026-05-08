import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("unlink")
@click.argument("model")
@click.option("--ids", required=True, help="Comma-separated IDs to unlink")
def unlink(model: str, ids: str) -> None:
    """Unlink (delete) records by IDs"""
    ensure_config_exists()
    client = OdooClient.from_config()
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    res = client.unlink(model, id_list)
    click.echo(json.dumps({"success": bool(res)}))
