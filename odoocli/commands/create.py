import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.click_types import JSON
from odoocli.tools.odoo_client import OdooClient


@click.command("create")
@click.argument("model")
@click.option(
    "--values",
    type=JSON(expected="list"),
    required=True,
    help=('JSON list of record objects to create. Example: \'[{"name": "A"}]\'.'),
)
def create(model: str, values) -> None:
    """Create multiple records in `model`"""
    ensure_config_exists()
    client = OdooClient.from_config()
    ids = client.create(model, values)
    click.echo(json.dumps({"ids": ids}, ensure_ascii=False))
