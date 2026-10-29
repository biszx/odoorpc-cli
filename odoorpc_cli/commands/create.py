import json

import click

from odoorpc_cli.tools import html_images
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
    field_meta = client.model_field(model)
    try:
        for record in values:
            for field in [f for f in record if html_images.is_html_field(field_meta, f)]:
                if record[field]:
                    record[field] = html_images.inline_images(record[field])
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    ids = client.create(model, values)
    click.echo(json.dumps({"ids": ids}, ensure_ascii=False))
