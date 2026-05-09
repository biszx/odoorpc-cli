import json

import click

from odoocli.settings import ensure_config_exists


@click.command("search")
@click.argument("query", required=True)
@click.pass_context
def model_search(ctx, query: str):
    """Search for models by name or substring `query`"""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    res = client.model_search(query)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
