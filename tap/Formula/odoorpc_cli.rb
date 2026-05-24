class OdoorpcCli < Formula
  include Language::Python::Virtualenv

  desc "Command-line tool for Odoo RPC"
  homepage "https://github.com/biszx/odoorpc_cli"
  version "1.2.1"
  url "https://files.pythonhosted.org/packages/source/o/odoorpc_cli/odoorpc_cli-#{version}.tar.gz"
  sha256 :no_check

  depends_on "python"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Odoo RPC CLI", shell_output("#{bin}/odoo --help")
  end
end
