import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.click_types import JSON
from odoocli.tools.odoo_client import OdooClient


@click.command("count")
@click.argument("model", required=True)
@click.option(
    "--domain",
    type=JSON(expected="list"),
    default=lambda: [],
    help=(
        'Odoo domain as a JSON list, e.g. \'[["name", "ilike", "test"]]\''
        " Defaults to an empty list (no filter)."
    ),
)
def search_count(model: str, domain: list):
    """Count records in `model` matching domain"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.search_count(model, domain)
    click.echo(json.dumps({"count": res}, indent=2, ensure_ascii=False))
