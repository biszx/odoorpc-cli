import click

from odoorpc_cli.tools import html_images
from odoorpc_cli.tools.click_types import JSON
from odoorpc_cli.tools.output import echo_json


@click.command("read")
@click.argument("model", required=True)
@click.option(
    "--domain",
    type=JSON(expected="list"),
    default=lambda: [],
    help=(
        'Odoo domain as a JSON list, e.g. \'[["name", "ilike", "test"]]\'.'
        " Defaults to an empty list (no filter)."
    ),
)
@click.option(
    "--fields",
    default="all",
    help=(
        "Comma-separated fields to read, e.g. 'name,email'."
        " Defaults to 'all' (all fields)."
    ),
)
@click.option(
    "--order",
    default=None,
    help="Order the results by field, e.g. 'name asc' or 'id desc'. Defaults to None (no ordering).",
)
@click.option(
    "--offset",
    type=int,
    default=0,
    help="Offset for pagination. Defaults to 0 (start from beginning).",
)
@click.option(
    "--limit",
    type=int,
    help="Limit the number of records returned. Defaults to None (no limit).",
)
@click.option(
    "--raw",
    is_flag=True,
    help=(
        "Keep embedded base64 images as-is. Without it, an html field's images are"
        " written to the image cache and their src replaced with a file:// path."
    ),
)
@click.pass_context
def search_read(
    ctx,
    model: str,
    domain,
    fields: str,
    order: str | None,
    offset: int,
    limit: int | None,
    raw: bool,
):
    """Search and read records from `model`"""
    client = ctx.obj.get("odoo")

    # prepare fields argument
    if fields == "all" or not fields:
        fields_arg = ["id"]
    else:
        fields_arg = [f.strip() for f in fields.split(",")]

    res = client.search_read(
        model, domain, fields_arg, order=order, offset=offset, limit=limit
    )
    if not raw:
        field_meta = client.model_field(model)
        html_fields = [f for f in fields_arg if html_images.is_html_field(field_meta, f)]
        if html_fields:
            html_images.prune_cache()
            for record in res:
                for field in html_fields:
                    if record.get(field):
                        record[field] = html_images.externalize_images(record[field])
    echo_json(res)
