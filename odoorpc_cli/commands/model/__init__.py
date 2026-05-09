import click

from .field import model_field
from .search import model_search


@click.group("model")
def model():
    """Model-introspection commands"""
    pass


model.add_command(model_field)
model.add_command(model_search)
