import click

from .login import login as auth_login
from .info import info as auth_info


@click.group("auth")
def auth():
    pass


auth.add_command(auth_login)
auth.add_command(auth_info)
