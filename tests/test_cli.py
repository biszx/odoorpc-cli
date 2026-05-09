from click.testing import CliRunner
from odoocli import __version__
from odoocli.cli import odoo


def test_version_and_help_options():
    runner = CliRunner()

    # --version should print the package version and exit successfully
    res = runner.invoke(odoo, ["--version"])
    assert res.exit_code == 0
    assert __version__ in res.output

    # -h should display help text and exit successfully
    res2 = runner.invoke(odoo, ["-h"])
    assert res2.exit_code == 0
    assert "Usage" in res2.output
