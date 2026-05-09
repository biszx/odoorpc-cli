# Domain docs and ADRs

Layout: Single-context

This repository uses a single `CONTEXT.md` at the repository root (if present) and a `docs/adr/` directory for architectural decision records.

Skills that read domain docs:

- `improve-codebase-architecture` — uses `CONTEXT.md` and `docs/adr/` to understand domain language and past decisions
- `diagnose` and `tdd` — consult `CONTEXT.md` for domain vocabulary and constraints

If you have a monorepo with multiple contexts, replace this with a `CONTEXT-MAP.md` that points to per-context `CONTEXT.md` files and per-context `docs/adr/` directories.
