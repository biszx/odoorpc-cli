import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.click_types import JSON


@click.command("write")
@click.argument("model")
@click.option("--id", "ids", required=True, help="Comma-separated id(s) to update")
@click.option(
    "--value",
    type=JSON(expected="dict"),
    required=True,
    help='JSON object of values to write to the records, e.g. \'{"name": "New"}\'.',
)
@click.pass_context
def write(ctx, model: str, ids: str, value) -> None:
    """Update records in `model`"""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    vals = value
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    ok = client.write(model, id_list, vals)
    click.echo(json.dumps({"success": bool(ok)}))
