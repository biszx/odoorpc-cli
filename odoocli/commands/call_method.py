import json

import click

from odoocli.tools.click_types import JSON


@click.command("call-method")
@click.argument("model")
@click.option("--method", required=True, help="Model method to call")
@click.option(
    "--args",
    type=JSON(expected="list"),
    default=lambda: [],
    help="JSON list of positional args, e.g. '[1, \"a\"]'. Defaults to an empty list.",
)
@click.option(
    "--kwargs",
    type=JSON(expected="dict"),
    default=lambda: {},
    help='JSON object of keyword args, e.g. \'{"key": "value"}\'.'
    " Defaults to an empty object.",
)
@click.pass_context
def call_method(ctx, model, method, args, kwargs):
    """Call a model method on `model`"""
    client = ctx.obj.get("odoo")
    res = client.execute_method(model, method, args=args, kwargs=kwargs)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
