import click

from .count import search_count
from .read import search_read


@click.group("search")
def search():
    """Search related commands"""
    pass


search.add_command(search_count)
search.add_command(search_read)
