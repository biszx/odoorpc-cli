import json

import click

from odoorpc_cli.tools.click_types import JSON


@click.command("write")
@click.argument("model")
@click.option(
    "--id",
    "ids",
    help="Comma-separated id(s) to update",
)
@click.option(
    "--domain",
    type=JSON(expected="list"),
    help=(
        "Odoo domain as a JSON list to select records to update, "
        "e.g. '[['name','ilike','Acme']]'"
    ),
)
@click.option(
    "--limit",
    type=int,
    help="Limit the number of records returned when using --domain. Defaults to None.",
)
@click.option(
    "--value",
    type=JSON(expected="dict"),
    required=True,
    help='JSON object of values to write to the records, e.g. \'{"name": "New"}\'.',
)
@click.pass_context
def write(
    ctx, model: str, ids: str | None, value, domain: list | None, limit: int | None
) -> None:
    """
    Update records in `model`.
    Provide either `--id` or `--domain` to search for records to update.
    When both are provided, the union of ids will be used.
    """
    client = ctx.obj.get("odoo")
    vals = value

    id_list: list[int] = []
    if ids:
        id_list.extend([int(x.strip()) for x in ids.split(",")])
    if domain is not None:
        # resolve ids from domain using search_read
        found = client.search_read(model, domain, ["id"], limit)
        id_list.extend([r["id"] for r in found])

    # deduplicate and normalize
    id_list = sorted(set(id_list))

    if not id_list:
        click.echo(json.dumps({"success": False, "ids": []}))
        return

    ok = client.write(model, id_list, vals)
    click.echo(json.dumps({"success": bool(ok)}))
