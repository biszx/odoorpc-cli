import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("field")
@click.argument("model", required=True)
def model_field(model: str):
    """Retrieve metadata for fields of `model`"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.model_field(model)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
