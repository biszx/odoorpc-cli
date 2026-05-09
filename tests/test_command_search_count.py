import odoocli.cli as cli_mod
from click.testing import CliRunner


def test_search_count_defaults_and_domain_parsing():
    runner = CliRunner()
    # Default domain (no --domain) should work
    res = runner.invoke(cli_mod.odoo, ["search", "count", "res.partner"])
    assert res.exit_code == 0
    assert '"count"' in res.output

    # Provide explicit domain as JSON string
    res2 = runner.invoke(
        cli_mod.odoo, ["search", "count", "res.partner", "--domain", "[]"]
    )
    assert res2.exit_code == 0
    assert '"count"' in res2.output
