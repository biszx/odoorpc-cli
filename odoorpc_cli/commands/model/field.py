import click

from odoorpc_cli.tools.output import echo_json


@click.command("field")
@click.argument("model", required=True)
@click.pass_context
def model_field(ctx, model: str):
    """Retrieve metadata for fields of `model`"""
    client = ctx.obj.get("odoo")
    echo_json(client.model_field(model))
