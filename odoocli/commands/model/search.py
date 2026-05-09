import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("search")
@click.argument("query", required=True)
def model_search(query: str):
    """Search for models by name or substring `query`"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.model_search(query)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
