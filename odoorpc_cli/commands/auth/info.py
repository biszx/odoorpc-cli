import click

from odoorpc_cli.tools.output import echo_json


@click.command("info")
@click.pass_context
def info(ctx):
    """Display information about the currently authenticated user."""
    client = ctx.obj.get("odoo")
    if client is None:
        click.echo("Not authenticated — run 'odoo auth login' to authenticate")
        return
    echo_json(client.get_current_user())
