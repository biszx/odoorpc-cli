# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Testing

Run the full suite from the repository root with exactly:

```bash
uv run pytest
```

Do not use `pytest`, `python -m pytest`, `tox`, or `poetry run pytest` — `uv run pytest` is the only sanctioned command. Details in `docs/agents/testing.md`.

Two test files fail on `develop` for reasons unrelated to current work, and have done for several releases:

- `tests/test_tools_version_check.py` and `tests/test_cli_update_warning.py` — both import `CACHE_FILE` from `odoorpc_cli.tools.version_check`, which no longer defines it; the module moved to `Settings.UPDATE_CHECK_PATH`.
- `tests/test_command_update.py::test_update_command_new_version_available` — asserts on the `uv tool upgrade` path, which does not apply on every install method.
- `tests/test_tools_odoo_client.py::test_connect_fetches_user_and_search_read` — its `FakeODOO.__init__` does not accept the `opener` kwarg the client passes.

When running a suite locally, expect these and do not treat them as regressions introduced by your change.

## Issue tracker

GitHub Issues. Labels are the default vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`.

## Releases

Releases are cut with git flow and published by CI — never by hand.

1. `git flow init -d` if the repo is not already initialized, then `git flow release start <version>`.
2. Bump the version with `./scripts/bump_version.sh <version>`. It updates both `odoorpc_cli/__init__.py` and `tap/Formula/odoorpc_cli.rb`. Check the two agree afterwards — they have drifted before, with the formula left behind.
3. Commit as `REL: Bump version to <version>`, then `GIT_EDITOR=true git flow release finish --no-ff -M "Merge branch 'release/<version>'" <version>`.
4. `git push origin main develop --tags`.

Pushing the tag is the whole release. `.github/workflows/release.yml` builds the Windows installer, publishes to PyPI, and generates the release notes with the opencode CLI, then creates the GitHub release from them.

**Do not run `gh release create`.** The workflow owns the release body; a manual release would carry notes the workflow then cannot replace.

### Secrets the release workflow needs

| Secret | Value |
| ------ | ----- |
| `OPENCODE_API_KEY` | OpenCode Console personal key, `oc_sk_...` |
| `OPENCODE_MODEL` | Provider-qualified model id, e.g. `opencode-go/mimo-v2.6-flash` |

The model must be provider-qualified — a bare model name is ambiguous across the provider catalog. The workflow fails fast with a message naming the secret if `OPENCODE_MODEL` is unset.

The notes prompt reads `docs/release-notes/TEMPLATE.md` and writes `release_artifacts/release_notes.md`; changing that template changes the shape of every published release body.
