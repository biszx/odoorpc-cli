import json

import click

from odoocli.settings import ensure_config_exists
from odoocli.tools.odoo_client import OdooClient


@click.command("call-method")
@click.argument("model")
@click.option("--method", required=True, help="Model method to call")
@click.option("--args", default="[]", help="JSON list of positional args")
@click.option("--kwargs", default="{}", help="JSON object of keyword args")
def call_method(model, method, args, kwargs):
    """Call a model method"""
    ensure_config_exists()
    client = OdooClient.from_config()
    args_obj = json.loads(args)
    kwargs_obj = json.loads(kwargs)
    res = client.execute_method(model, method, args=args_obj, kwargs=kwargs_obj)
    click.echo(json.dumps(res, indent=2, ensure_ascii=False))
