class Odoocli < Formula
  include Language::Python::Virtualenv

  desc "Command-line tool for Odoo"
  homepage "https://github.com/biszx/odoocli"
  # When you release a version, upload the sdist to PyPI and update the
  # `url` and `sha256` to point at the sdist for that version.
  url "https://files.pythonhosted.org/packages/source/o/odoocli/odoocli-0.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Odoo CLI", shell_output("#{bin}/odoo --help")
  end
end
