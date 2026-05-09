# Agents and tooling

## Agent skills

### Issue tracker

This repository uses GitHub Issues as its issue tracker. See `docs/agents/issue-tracker.md`.

### Triage labels

The repository uses the default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Layout: single-context — a `CONTEXT.md` at the repo root and `docs/adr/` for ADRs. See `docs/agents/domain.md`.

### Testing

AI agents should run the repository test suite using the project's environment wrapper. See `docs/agents/testing.md` for the required command and guidance.
