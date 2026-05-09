import click

from odoocli import __version__
from odoocli.commands import auth, call_method, create, model, search, unlink, write


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="odoocli")
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
