import json

import click


@click.command("field")
@click.argument("model", required=True)
@click.pass_context
def model_field(ctx, model: str):
    """Retrieve metadata for fields of `model`"""
    client = ctx.obj.get("odoo")
    res = client.model_field(model)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
