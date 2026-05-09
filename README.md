# Odoo RPC CLI

A command-line interface for Odoo, providing quick access to common operations like authentication, searching, creating, updating, and deleting records. It is designed for AI, developers and administrators who prefer working in the terminal.

## Installation

### Homebrew (tap)

Install `odoorpc_cli` from the project's Homebrew tap (recommended):

```bash
brew tap biszx/tap https://github.com/biszx/homebrew-tap
brew install biszx/tap/odoorpc_cli
```

### Windows

Standalone executable (no Python required): download the `odoorpc_cli` Windows executable from a release's assets (the repository contains a CI workflow that builds an exe with PyInstaller and uploads it as an artifact). Place the exe on `PATH` or run it directly.

Installer (recommended): download the Inno Setup installer (`odoorpc_cli-X.Y.Z-setup.exe`) from a release's assets — it creates shortcuts and an uninstaller for easy setup on Windows.

### Python (pip)

Install from PyPI:

```bash
pip install odoorpc_cli
```

## Usage

Authenticate and save credentials (interactive):

```
odoo auth login --host https://odoo.example.com --db demo --username admin --password secret
```

Search for records:

```
odoo search read res.partner --domain "[[\"name\", \"ilike\", \"Acme\"]]" --fields name,email
```

Call a custom model method:

```
odoo call-method res.partner --method custom_method --args "[]" --kwargs "{}"
```

## Contributing

Please open issues and pull requests on the repository. Run tests with `pytest`.
