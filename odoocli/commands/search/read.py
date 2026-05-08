import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("read")
@click.argument("model", required=True)
@click.option(
    "--domain",
    default="[]",
    help=(
        "Odoo domain as a JSON string, e.g. '[('name', 'ilike', 'test')]'."
        " Defaults to '[]' (no filter)."
    ),
)
@click.option(
    "--fields",
    default="all",
    help=(
        "Comma-separated fields to read, e.g. 'name,email'."
        " Defaults to 'all' (all fields)."
    ),
)
@click.option(
    "--limit",
    default=None,
    help="Limit the number of records returned. Defaults to None (no limit).",
)
def search_read(model: str, domain: str, fields: str, limit: int | None):
    """Search and read records from a model"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.search_read(model, domain, fields, limit)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
