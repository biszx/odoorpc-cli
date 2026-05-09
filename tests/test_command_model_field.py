from click.testing import CliRunner
from odoorpc_cli.cli import odoo


def test_model_field_res_partner():
    runner = CliRunner()
    res = runner.invoke(odoo, ["model", "field", "res.partner"])
    assert res.exit_code == 0
    assert "name" in res.output
