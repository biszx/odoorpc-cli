import json

import click

from odoorpc_cli.tools.click_types import JSON


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
    type=int,
    help="Limit the number of records returned. Defaults to None (no limit).",
)
@click.pass_context
def search_read(ctx, model: str, domain, fields: str, limit: int | None):
    """Search and read records from `model`"""
    client = ctx.obj.get("odoo")

    # prepare fields argument
    if fields == "all" or not fields:
        fields_arg = ["id"]
    else:
        fields_arg = [f.strip() for f in fields.split(",")]

    res = client.search_read(model, domain, fields_arg, limit)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
