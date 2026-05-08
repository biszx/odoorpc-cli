import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("info")
def info():
    """Show information of the authenticated user"""
    ensure_config_exists()
    client = OdooClient.from_config()
    res = client.get_current_user()
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
