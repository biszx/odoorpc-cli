import json

import click

from odoorpc_cli.tools.click_types import JSON


@click.command("create")
@click.argument("model")
@click.option(
    "--values",
    type=JSON(expected="list"),
    required=True,
    help=('JSON list of record objects to create. Example: \'[{"name": "A"}]\'.'),
)
@click.pass_context
def create(ctx, model: str, values) -> None:
    """Create multiple records in `model`"""
    client = ctx.obj.get("odoo")
    ids = client.create(model, values)
    click.echo(json.dumps({"ids": ids}, ensure_ascii=False))
