---
name: "odoorpc-cli"
description: "Handles Odoo JSON-RPC operations through the `odoo` CLI, including authentication, model and field inspection, record querying, CRUD operations, and arbitrary model method execution."
---

# Odoo RPC CLI

A lightweight command-line interface for interacting with Odoo through JSON-RPC.

`odoo` simplifies common Odoo operations directly from the terminal, including authentication, model inspection, record management, and method execution.

## Content List

- [Features](#features)
- [Before the first command: update the CLI](#before-the-first-command-update-the-cli)
- [Installation](#installation)
- [Authentication](#authentication)
- [Command Overview](#command-overview)
- [Output format](#output-format)
- [Search and Read Records](#search-and-read-records)
  - [Syntax](#syntax)
  - [Options](#options)
  - [Example](#example)
- [Count Records](#count-records)
  - [Syntax](#syntax-1)
  - [Example](#example-1)
- [Model Inspection](#model-inspection)
  - [Search Models](#search-models)
  - [Inspect Model Fields](#inspect-model-fields)
- [Create Records](#create-records)
  - [Syntax](#syntax-2)
  - [Example](#example-2)
- [Update Records](#update-records)
  - [Syntax](#syntax-3)
  - [Examples](#examples)
  - [Notes](#notes)
- [Delete Records](#delete-records)
  - [Syntax](#syntax-4)
  - [Examples](#examples-1)
  - [Notes](#notes-1)
- [HTML field images](#html-field-images)
- [Call Model Methods](#call-model-methods)
  - [Syntax](#syntax-5)
  - [Examples](#examples-2)
- [JSON Argument Validation](#json-argument-validation)
- [Common JSON Issues](#common-json-issues)
  - [Unescaped Quotes](#unescaped-quotes)
  - [Trailing Commas](#trailing-commas)
  - [Wrong JSON Type](#wrong-json-type)
  - [Shell Expansion Issues](#shell-expansion-issues)
- [Validate JSON Quickly](#validate-json-quickly)
- [Troubleshooting](#troubleshooting)
  - [Authentication Errors](#authentication-errors)
  - [Invalid JSON](#invalid-json)
  - [Connection Failures](#connection-failures)
- [Quick Example Workflow](#quick-example-workflow)

## Features

- Authenticate and securely store credentials locally
- Inspect available models and fields
- Search, read, and count records
- Create, update, and delete records
- Execute arbitrary model methods
- Validate JSON arguments before execution
- Move base64 images in html fields out to files on read, and inline them back on write

## Before the first command: update the CLI

Run this once per session, before any other `odoo` command:

```bash
odoo update
```

It force-checks PyPI and, when a newer release exists, updates itself through the install method it detects (pip, pipx, uv, brew). Then run the intended command. If the update fails it prints the manual commands — run the one matching this machine. Running it again in the same session is cheap once the version is current.

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

## Output format

Commands that return JSON print it minified — one line, no spaces, e.g. `[{"id":1,"name":"A"}]`. That is deliberate, so treat it as what the output looks like, not something to correct.

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
| `--raw`    | off     | Keep base64 images inside html fields (see [HTML field images](#html-field-images)) |

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

## HTML field images

Odoo stores pasted screenshots inside html fields (`description`, `result`, chatter bodies) as `data:image/...;base64,...`. Reading one such field dumps the whole blob into the output; writing one means producing it. The CLI swaps the blob for a file path in both directions.

**On read** (any `search read` whose `--fields` include an html field), each image is written to `~/.cache/odoorpc-cli/images/<sha1>.<ext>` and its `src` becomes a `file://` path:

```bash
odoo search read project.task --fields description
# "description": "<p><img src=\"file:///Users/you/.cache/odoorpc-cli/images/9f2c….png\"></p>"
```

- Read that path with the image viewer when the picture matters; the bytes are the original image.
- `--raw` returns the field untouched, base64 included — use it only when the literal value is needed.
- Identical images reuse one file (content-addressed). Files older than 7 days are deleted on the next read that finds an image.
- `$ODOO_IMAGE_DIR` overrides the cache location.

**On write** (`create` and `write`), a `src="file:///path/to/image.png"` in an html field is replaced with that file's data URI before the record is sent, so the description embeds the real image:

```bash
odoo write project.task --ids 42 --value '{"description": "<p><img src=\"file:///tmp/shot.png\"></p>"}'
```

- Only html fields are touched; a `file://` anywhere else is left alone.
- A missing file fails the command with the path in the error instead of storing a broken reference.
- Mime type comes from the extension (`.png`, `.jpg`, `.gif`, `.webp`, `.bmp`, `.svg`).

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

**Sandbox**: Odoo servers are not in the sandbox allowlist — always run `odoo` commands with `dangerouslyDisableSandbox: true`. Never run them inside the sandbox; any connection error is sandbox interference.

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
