import json

import click

from odoocli.settings import ensure_config_exists


@click.command("unlink")
@click.argument("model")
@click.option(
    "--ids",
    required=True,
    help="Comma-separated record IDs to unlink (delete), e.g. '1,2,3'.",
)
@click.pass_context
def unlink(ctx, model: str, ids: str) -> None:
    """Delete records in `model`"""
    ensure_config_exists()
    client = ctx.obj.get("odoo")
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    res = client.unlink(model, id_list)
    click.echo(json.dumps({"success": bool(res)}))
