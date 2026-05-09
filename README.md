# Odoo CLI

A command-line interface for Odoo, providing quick access to common operations like authentication, searching, creating, updating, and deleting records. It is designed for AI, developers and administrators who prefer working in the terminal.

## Installation

### MacOS/Linux:

```
brew install odoocli
```

### Python package:

```
pip install odoocli
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
