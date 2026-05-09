import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.click_types import JSON


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
@click.pass_context
def search_count(ctx, model: str, domain: list):
    """Count records in `model` matching domain"""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    res = client.search_count(model, domain)
    click.echo(json.dumps({"count": res}, indent=2, ensure_ascii=False))
