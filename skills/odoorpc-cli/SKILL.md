---
name: odoorpc-cli
description: Detailed usage guide for the `odoo` CLI. Includes examples for authentication, searching, creating, updating, deleting records, and calling model methods.
metadata:
  version: 1.1.0
  category: meta
---

## Overview

`odoo` is a small command-line wrapper around an Odoo JSON-RPC client that lets you:

- Authenticate and persist credentials locally (`odoo auth login`).
- Introspect models and fields (`odoo model search`, `odoo model field`).
- Search and read records (`odoo search read`, `odoo search count`).
- Create, update, and delete records (`odoo create`, `odoo write`, `odoo unlink`).
- Call arbitrary model methods (`odoo call-method`).

## Quickstart

1. Install the package:

```bash
pip install odoorpc-cli
```

2. Verify the CLI is available:

```bash
odoo --version
```

3. Authenticate with user Odoo server:

Ask the user to manually run the login command and provide connection details:

```bash
odoo auth login
```

The `login` command can be passed as options or prompts for `host`, `db`, `username` and `password`.

If you try to run other commands without authenticating, the CLI will print `Not authenticated — run 'odoo auth login' to authenticate` and exit.

## Command reference & examples

Notes on quoting: many options accept JSON values. Use single quotes around JSON on POSIX shells to avoid expansion, for example `'[{"a": 1}]'`. If your JSON contains single quotes, use double quotes and escape as needed, or use a here-doc.

### Authentication

**Authenticate with the Odoo server and manage credentials.**

```bash
odoo auth login
```

passed as options or prompts for `host`, `db`, `username`, and `password` (input hidden).

**Show current user authentication info.**

```bash
odoo auth info
```

### Search and read records

**Search for records matching a domain, read specified fields, and print results as JSON.**

```bash
odoo search read <model> --domain '<domain-json>' --fields <field1,field2> --limit N
```

Example:

```bash
odoo search read res.partner --domain '[ ["name", "ilike", "Acme"] ]' --fields name,email --limit 10
```

**Count records matching a domain.**

```bash
odoo search count <model> --domain '<domain-json>'
```

Example:

```bash
odoo search count res.partner --domain '[ ["is_company", "=", true] ]'
```

### Model

**Find models by name or technical name.**

```bash
odoo model search <query>
```

Example:

```bash
odoo model search partner
```

**Returns metadata for fields of `model`**

```bash
odoo model field <model>
```

Example:

```bash
odoo model field res.partner
```

### Create

**Create new records in a model.**

```bash
odoo create <model> --values '<json-list>'
```

`--values` expects a JSON list of objects. Example:

```bash
odoo create res.partner --values '[{"name": "New Co", "email": "x@example.com"}]'
```

### Update records

**Update existing records in a model.**

```bash
odoo write <model> --id '<id[,id...]>' --value '<json-object>'
```

- `--id` accepts comma-separated IDs (example: `'1,2,3'`).
- `--value` expects a JSON object of field values. Example:

```bash
odoo write res.partner --id '42' --value '{"name": "Renamed Co"}'
odoo write res.partner --id '41,42' --value '{"active": false}'
```

### Delete records

**Delete records in a model.**

```bash
odoo unlink <model> --ids '<id[,id...]>'
```

- Example:

```bash
odoo unlink res.partner --ids '99'
```

### Call method

**Call arbitrary model methods.**

```bash
odoo call-method <model> --method <method_name> --args '<json-list>' --kwargs '<json-object>'
```

Example (positional args):

```bash
odoo call-method res.partner --method name_get --args '[42]'
```

Example (kwargs):

```bash
odoo call-method sale.order --method action_confirm --args '[1]' --kwargs '{}'
```

## Argument types and validation

This CLI uses a small `JSON` click `ParamType` for JSON options. The parameter type validates whether the provided JSON parses and matches the expected shape (`list` or `dict`).

- `--domain` expects a JSON list (domain list).
- `--values` expects a JSON list of record objects (for `create`).
- `--value` expects a JSON object (for `write`).
- `--args` expects a JSON list (positional arguments for `call-method`).
- `--kwargs` expects a JSON object (keyword arguments for `call-method`).

If the CLI prints `Failed to parse JSON: ...`, re-check quoting and JSON validity.

## Troubleshooting

- Not authenticated: run `odoo auth login` (the CLI aborts other commands when not authenticated).
- Invalid JSON: check quoting and use `python -c 'import json; print(json.loads("<your-json>") )'` to validate quickly.
- Connection/auth failures: verify `host`, `db`, `username`, and `password` are correct and that the Odoo server is reachable.
