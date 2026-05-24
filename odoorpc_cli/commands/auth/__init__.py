import click

from .info import info as auth_info
from .login import login as auth_login
from .logout import logout as auth_logout


@click.group("auth")
def auth():
    """Authentication related commands"""
    pass


auth.add_command(auth_login)
auth.add_command(auth_info)
auth.add_command(auth_logout)

