import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.click_types import JSON


@click.command("read")
@click.argument("model", required=True)
@click.option(
    "--domain",
    type=JSON(expected="list"),
    default=lambda: [],
    help=(
        'Odoo domain as a JSON list, e.g. \'[["name", "ilike", "test"]]\'.'
        " Defaults to an empty list (no filter)."
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
@click.pass_context
def search_read(ctx, model: str, domain, fields: str, limit: int | None):
    """Search and read records from `model`"""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    res = client.search_read(model, domain, fields, limit)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
