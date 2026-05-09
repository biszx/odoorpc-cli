import click

from odoocli.settings import Settings
from odoocli.tools.odoo_client import OdooClient


@click.command("login")
@click.option(
    "--host",
    prompt="Odoo server base URL",
    help="Odoo server base URL, e.g. http://localhost:8069",
)
@click.option("--db", prompt="Odoo database name", help="Odoo database name")
@click.option("--username", prompt="Odoo username", help="Odoo username")
@click.option(
    "--password",
    prompt="Odoo password",
    hide_input=True,
    confirmation_prompt=True,
    help="Odoo API key or password",
)
def login(host, db, username, password):
    """Authenticate and save Odoo connection settings."""
    OdooClient(host=host, db=db, username=username, password=password)
    Settings.save(host=host, db=db, username=username, password=password)
    click.echo("Login successful!")
