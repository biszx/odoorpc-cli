import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("info")
@click.pass_context
def info(ctx):
    """Display information about the currently authenticated user."""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    if client is None:
        click.echo("Not authenticated — run 'odoo auth login' to authenticate")
        return
    res = client.get_current_user()
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
