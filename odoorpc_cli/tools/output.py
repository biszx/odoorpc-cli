import json

import click


def echo_json(data) -> None:
    """Print `data` as JSON, minified unless the group's --pretty flag was passed."""
    ctx = click.get_current_context(silent=True)
    pretty = bool(ctx and ctx.obj and ctx.obj.get("pretty"))
    if pretty:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        click.echo(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
