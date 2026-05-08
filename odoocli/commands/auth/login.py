import click

from odoocli.settings import ensure_config_exists, save_config
from odoocli.tools.odoo_client import OdooClient


@click.command("login")
@click.option(
    "--host", prompt=True, help="Odoo server base URL, e.g. http://localhost:8069"
)
@click.option("--db", prompt=True, help="Odoo database name")
@click.option("--username", prompt=True, help="Odoo username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Odoo API key or password",
)
def login(host, db, username, password):
    """Login to Odoo"""
    ensure_config_exists()
    OdooClient(host=host, db=db, username=username, password=password)
    save_config(host=host, db=db, username=username, password=password)
    click.echo("Login successful!")
