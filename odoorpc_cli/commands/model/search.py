import click

from odoorpc_cli.tools.output import echo_json


@click.command("search")
@click.argument("query", required=True)
@click.pass_context
def model_search(ctx, query: str):
    """Search for models by name or substring `query`"""
    client = ctx.obj.get("odoo")
    echo_json(client.model_search(query))
