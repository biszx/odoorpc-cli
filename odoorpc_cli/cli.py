import click

from odoorpc_cli import __version__
from odoorpc_cli.commands import (
    auth,
    call_method,
    create,
    model,
    search,
    unlink,
    update,
    write,
)
from odoorpc_cli.tools.odoo_client import OdooClient
from odoorpc_cli.tools.version_check import check_for_updates


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="odoorpc_cli")
@click.pass_context
def odoo(ctx):
    """Odoo RPC CLI - interact with your Odoo instance from the command line"""
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != "update":
        try:
            is_avail, latest = check_for_updates()
            if is_avail:
                click.secho(
                    (
                        f"WARNING: A new version of odoorpc-cli is available:"
                        f" {latest} (current: {__version__})."
                    ),
                    fg="yellow",
                    err=True,
                )
                click.secho(
                    "To update, run 'odoo update' or 'pip install -U odoorpc-cli'.\n",
                    fg="yellow",
                    err=True,
                )
        except Exception:
            pass

    try:
        ctx.obj["odoo"] = OdooClient.from_config()
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
odoo.add_command(update)
odoo.add_command(call_method)


if __name__ == "__main__":
    odoo(obj={})  # pragma: no cover - script entrypoint
