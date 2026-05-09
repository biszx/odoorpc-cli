import json

import click

from odoorpc_cli.tools.click_types import JSON


@click.command("unlink")
@click.argument("model")
@click.option(
    "--ids",
    help="Comma-separated record IDs to unlink (delete), e.g. '1,2,3'.",
)
@click.option(
    "--domain",
    type=JSON(expected="list"),
    help=(
        "Odoo domain as a JSON list to select records to unlink, "
        "e.g. '[['active', '=', false]]'"
    ),
)
@click.option(
    "--limit",
    type=int,
    help="Limit the number of records returned when using --domain. Defaults to None.",
)
@click.pass_context
def unlink(
    ctx, model: str, ids: str | None, domain: list | None, limit: int | None
) -> None:
    """
    Delete records in `model`.
    Provide either `--ids` or `--domain` to select records.
    When both are provided, the union of ids will be used.
    """
    client = ctx.obj.get("odoo")

    id_list: list[int] = []
    if ids:
        id_list.extend([int(x.strip()) for x in ids.split(",")])

    if domain is not None:
        found = client.search_read(model, domain, ["id"], limit)
        id_list.extend([r["id"] for r in found])

    id_list = sorted(set(id_list))

    if not id_list:
        click.echo(json.dumps({"success": False, "ids": []}))
        return

    res = client.unlink(model, id_list)
    click.echo(json.dumps({"success": bool(res)}))
