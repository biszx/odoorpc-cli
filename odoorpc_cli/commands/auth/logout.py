import os

import click

from odoorpc_cli.settings import Settings


@click.command("logout")
def logout():
    """Log out and remove saved Odoo connection settings."""
    if not os.path.isfile(Settings.CONFIG_PATH):
        click.echo("Not authenticated — run 'odoo auth login' to authenticate")
        return

    Settings.clear()
    click.echo("Successfully logged out.")
