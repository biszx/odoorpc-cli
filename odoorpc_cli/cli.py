import click

from odoorpc_cli import __version__
from odoorpc_cli.commands import auth, call_method, create, model, search, unlink, write
from odoorpc_cli.tools.odoo_client import odoorpc_client


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="odoorpc_cli")
@click.pass_context
def odoo(ctx):
    """Odoo CLI - interact with your Odoo instance from the command line"""
    ctx.ensure_object(dict)
    try:
        ctx.obj["odoo"] = odoorpc_client.from_config()
    except Exception:
        ctx.obj["odoo"] = None
        if ctx.invoked_subcommand != "auth":
            click.echo("Not authenticated — run 'odoo auth login' to authenticate")
            ctx.exit(1)


odoo.add_command(auth)
odoo.add_command(model)
odoo.add_command(search)
odoo.add_command(create)
odoo.add_command(write)
odoo.add_command(unlink)
odoo.add_command(call_method)


if __name__ == "__main__":
    odoo(obj={})  # pragma: no cover - script entrypoint
