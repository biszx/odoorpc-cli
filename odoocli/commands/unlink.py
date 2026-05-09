import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("unlink")
@click.argument("model")
@click.option(
    "--ids",
    required=True,
    help="Comma-separated record IDs to unlink (delete), e.g. '1,2,3'.",
)
def unlink(model: str, ids: str) -> None:
    """Delete records in `model`"""
    ensure_config_exists()
    client = OdooClient.from_config()
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    res = client.unlink(model, id_list)
    click.echo(json.dumps({"success": bool(res)}))
