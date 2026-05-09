import odoocli.cli as cli_mod
from click.testing import CliRunner


def test_model_search_command_outputs_models():
    runner = CliRunner()
    res = runner.invoke(cli_mod.odoo, ["model", "search", "partner"])
    assert res.exit_code == 0
    assert '"models"' in res.output
