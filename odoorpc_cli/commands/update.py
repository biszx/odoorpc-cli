import subprocess
import sys

import click

from odoorpc_cli import __version__
from odoorpc_cli.tools.version_check import check_for_updates


def get_update_command() -> list[str]:
    exe_path = sys.executable.lower()
    # 1. Check for Homebrew
    if "cellar" in exe_path or "homebrew" in exe_path:
        return ["brew", "upgrade", "odoorpc_cli"]
    # 2. Check for UV tool
    if "uv" in exe_path or ".local/share/uv" in exe_path:
        return ["uv", "tool", "upgrade", "odoorpc-cli"]
    # 3. Check for pipx
    if "pipx" in exe_path or ".local/share/pipx" in exe_path:
        return ["pipx", "upgrade", "odoorpc-cli"]
    # 4. Default to pip
    return [sys.executable, "-m", "pip", "install", "-U", "odoorpc-cli"]


@click.command("update")
def update() -> None:
    """Check for new versions of odoorpc-cli and perform the update."""
    click.echo("Checking for updates...")
    is_avail, latest = check_for_updates(force=True)
    if is_avail:
        click.secho(
            (
                f"A new version of odoorpc-cli is available: {latest}"
                f" (current: {__version__})."
            ),
            fg="yellow",
            bold=True,
        )

        cmd = get_update_command()
        click.echo(f"Running: {' '.join(cmd)}\n")
        try:
            subprocess.run(cmd, check=True)
            click.secho("\nSuccessfully updated odoorpc-cli!", fg="green")
        except Exception as e:
            click.secho(f"\nFailed to execute automatic update: {e}", fg="red")
            click.echo("Please run one of the commands manually to update:")
            click.secho("  pip install -U odoorpc-cli", fg="cyan")
            click.secho("  pipx upgrade odoorpc-cli", fg="cyan")
            click.secho("  uv tool upgrade odoorpc-cli", fg="cyan")
            click.secho("  brew upgrade biszx/odoorpc-cli/odoorpc_cli", fg="cyan")
            click.echo("")
    else:
        click.secho(f"odoorpc-cli is up to date (version {__version__}).", fg="green")
