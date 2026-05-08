import click

from .commands.auth import auth
from .commands.call_method import call_method
from .commands.create import create
from .commands.model import model
from .commands.search import search
from .commands.unlink import unlink
from .commands.write import write


@click.group()
def odoo():
    """Odoo CLI - interact with your Odoo instance from the command line"""
    pass


odoo.add_command(auth)
odoo.add_command(model)
odoo.add_command(search)
odoo.add_command(create)
odoo.add_command(write)
odoo.add_command(unlink)
odoo.add_command(call_method)


if __name__ == "__main__":
    odoo()
