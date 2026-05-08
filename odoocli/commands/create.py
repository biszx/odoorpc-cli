import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("create")
@click.argument("model")
@click.option("--values", required=True, help="Multiple records as JSON list string")
def create(model: str, values: str) -> None:
    """Create multiple records."""
    ensure_config_exists()
    client = OdooClient.from_config()

    try:
        vals_list = json.loads(values)
    except Exception:
        click.echo("Failed to parse --values as JSON list", err=True)
        raise

    if not isinstance(vals_list, list):
        raise click.BadParameter("--values must be a JSON list of objects")

    ids = client.create(model, vals_list)
    click.echo(json.dumps({"ids": ids}))
