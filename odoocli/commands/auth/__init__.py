import click

from .info import info as auth_info
from .login import login as auth_login


@click.group("auth")
def auth():
    """Authentication related commands"""
    pass


auth.add_command(auth_login)
auth.add_command(auth_info)
