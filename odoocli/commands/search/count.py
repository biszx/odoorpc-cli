import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("count")
@click.argument("model", required=True)
@click.option(
    "--domain",
    default="[]",
    help=(
        "Odoo domain as a JSON string, e.g. '[('name', 'ilike', 'test')]'."
        " Defaults to '[]' (no filter)."
    ),
)
def search_count(model: str, domain: str):
    """Count records matching a domain"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.search_count(model, domain)
    click.echo(json.dumps({"count": res}, indent=2, ensure_ascii=False))
