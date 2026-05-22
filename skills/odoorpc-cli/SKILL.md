---
name: odoorpc-cli
description: Handles Odoo JSON-RPC operations through the `odoo` CLI, including authentication, model and field inspection, record querying, CRUD operations, and arbitrary model method execution.
metadata:
  version: 1.1.0
  category: meta
---

# Odoo RPC CLI

A lightweight command-line interface for interacting with Odoo through JSON-RPC.

`odoo` simplifies common Odoo operations directly from the terminal, including authentication, model inspection, record management, and method execution.

## Features

- Authenticate and securely store credentials locally
- Inspect available models and fields
- Search, read, and count records
- Create, update, and delete records
- Execute arbitrary model methods
- Validate JSON arguments before execution

## Installation

Install the package using pip:

```bash
pip install odoorpc-cli
```

Verify the installation:

```bash
odoo --version
```

## Authentication

Authenticate against your Odoo server before using other commands:

```bash
odoo auth login
```

You will be prompted for:

- Host
- Database
- Username
- Password

You may also provide these values through command options.

Check the current authenticated session:

```bash
odoo auth info
```

If authentication has not been configured, the CLI will return:

```text
Not authenticated — run 'odoo auth login' to authenticate
```

## Command Overview

| Category       | Command             | Description                         |
| -------------- | ------------------- | ----------------------------------- |
| Authentication | `odoo auth login`   | Authenticate with the Odoo server   |
| Authentication | `odoo auth info`    | Show current authentication details |
| Search         | `odoo search read`  | Search and retrieve records         |
| Search         | `odoo search count` | Count matching records              |
| Model          | `odoo model search` | Search available models             |
| Model          | `odoo model field`  | Display model field metadata        |
| Records        | `odoo create`       | Create new records                  |
| Records        | `odoo write`        | Update existing records             |
| Records        | `odoo unlink`       | Delete records                      |
| Methods        | `odoo call-method`  | Execute arbitrary model methods     |

## Search and Read Records

Search for records matching a domain and return selected fields.

### Syntax

```bash
odoo search read <model> --domain '<domain-json>' --fields <field1,field2> --order '<field dir>' --offset N --limit N
```

### Options

| Option     | Default | Description                                     |
| ---------- | ------- | ----------------------------------------------- |
| `--domain` | `[]`    | JSON array Odoo domain filter                   |
| `--fields` | `all`   | Comma-separated fields; `all` returns only `id` |
| `--order`  | None    | Sort expression, e.g. `name asc` or `id desc`   |
| `--offset` | `0`     | Number of records to skip (for pagination)      |
| `--limit`  | None    | Maximum number of records to return             |

### Example

```bash
odoo search read res.partner \
  --domain '[["name", "ilike", "Acme"]]' \
  --fields name,email \
  --order 'name asc' \
  --offset 0 \
  --limit 10
```

#### Paginate through results

```bash
# Page 1
odoo search read res.partner --fields name,email --limit 20 --offset 0

# Page 2
odoo search read res.partner --fields name,email --limit 20 --offset 20
```

## Count Records

Return the number of records matching a domain.

### Syntax

```bash
odoo search count <model> --domain '<domain-json>'
```

### Example

```bash
odoo search count res.partner \
  --domain '[["is_company", "=", true]]'
```

## Model Inspection

### Search Models

Find models by technical name or keyword.

#### Syntax

```bash
odoo model search <query>
```

#### Example

```bash
odoo model search partner
```

### Inspect Model Fields

Display metadata for all fields in a model.

#### Syntax

```bash
odoo model field <model>
```

#### Example

```bash
odoo model field res.partner
```

## Create Records

Create one or more records in a model.

### Syntax

```bash
odoo create <model> --values '<json-list>'
```

### Example

```bash
odoo create res.partner \
  --values '[{"name": "New Co", "email": "x@example.com"}]'
```

`--values` must be a JSON array containing one or more record objects.

## Update Records

Update existing records by ID or domain.

### Syntax

```bash
odoo write <model> --ids '<id[,id...]>' --value '<json-object>'
odoo write <model> --domain '<domain-json>' --value '<json-object>' --limit N
```

### Examples

Update a single record by id:

```bash
odoo write res.partner \
  --ids '42' \
  --value '{"name": "Renamed Co"}'
```

Update multiple records by id:

```bash
odoo write res.partner \
  --ids '41,42' \
  --value '{"active": false}'
```

Update records by domain:

```bash
odoo write res.partner \
  --domain '[ ["name","ilike","Acme"] ]' \
  --value '{"active": false}' \
  --limit 10
```

### Notes

- `--ids` accepts comma-separated IDs
- `--value` must be a JSON object
- `--domain` accepts a JSON array (Odoo domain) and is resolved to matching IDs; use `--limit` to bound results when using `--domain`. When both `--id` and `--domain` are provided, the union of IDs will be used.

## Delete Records

Delete records from a model.

### Syntax

```bash
odoo unlink <model> --ids '<id[,id...]>'
odoo unlink <model> --domain '<domain-json>' --limit N
```

### Examples

```bash
odoo unlink res.partner --ids '99'
```

Delete records by domain:

```bash
odoo unlink res.partner \
  --domain '[["is_company","=",true]]' \
  --limit 50
```

### Notes

- `--ids` accepts comma-separated IDs
- `--domain` accepts a JSON array (Odoo domain). Use `--limit` to bound results when using `--domain`.
- When both `--ids` and `--domain` are provided, the union of IDs will be used.

## Call Model Methods

Execute arbitrary model methods with positional and keyword arguments.

### Syntax

```bash
odoo call-method <model> \
  --method <method_name> \
  --args '<json-list>' \
  --kwargs '<json-object>'
```

### Examples

#### Positional Arguments

```bash
odoo call-method res.partner \
  --method name_get \
  --args '[42]'
```

#### Keyword Arguments

```bash
odoo call-method sale.order \
  --method action_confirm \
  --args '[1]' \
  --kwargs '{}'
```

## JSON Argument Validation

Several commands accept JSON input. The CLI validates the structure before execution.

| Argument   | Expected Type |
| ---------- | ------------- |
| `--domain` | JSON array    |
| `--values` | JSON array    |
| `--value`  | JSON object   |
| `--args`   | JSON array    |
| `--kwargs` | JSON object   |

## Common JSON Issues

### Unescaped Quotes

#### Problem

```text
Failed to parse JSON
```

#### Solution

Wrap JSON with single quotes:

```bash
--domain '[["name", "=", "O'Reilly"]]'
```

Or escape quotes properly:

```bash
--domain "[[\"name\", \"=\", \"O'Reilly\"]]"
```

### Trailing Commas

#### Problem

Invalid JSON syntax caused by trailing commas.

#### Solution

Remove trailing commas from arrays and objects.

### Wrong JSON Type

#### Problem

Passing an object instead of a list, or vice versa.

#### Solution

Use:

- `[]` for arrays
- `{}` for objects

### Shell Expansion Issues

#### Problem

Shell interprets special characters unexpectedly.

#### Solution

Always quote JSON arguments.

## Validate JSON Quickly

Use Python to verify JSON syntax:

```bash
python -c 'import json; print(json.loads("<your-json>"))'
```

## Troubleshooting

### Authentication Errors

Ensure:

- Host is reachable
- Database name is correct
- Username and password are valid

Re-authenticate if necessary:

```bash
odoo auth login
```

### Invalid JSON

Verify:

- Quotes are escaped correctly
- Arrays and objects are valid JSON
- JSON values are properly quoted

### Connection Failures

Check:

- Network connectivity
- Odoo server availability
- Firewall or VPN restrictions

## Quick Example Workflow

```bash
# Authenticate
odoo auth login

# Search records
odoo search read res.partner \
  --domain '[["is_company", "=", true]]' \
  --fields name,email

# Create a record
odoo create res.partner \
  --values '[{"name": "Example Co"}]'

# Update a record
odoo write res.partner \
  --ids '42' \
  --value '{"active": false}'

# Delete a record
odoo unlink res.partner --ids '42'

# Delete records by domain
odoo unlink res.partner \
  --domain '[["is_company","=",true]]'
```
