# Agent testing policy

## Purpose

This document tells AI agents how to run and verify tests for this repository.

## Policy

- Always run the full test suite from the repository root using the exact command:
  ```bash
  uv run pytest
  ```
- Do not run other test commands (for example: `pytest`, `python -m pytest`, `tox`, or `poetry run pytest`).
- Ensure you are at the repository root before running `uv run pytest`.
- If tests fail, inspect failures and fix code or tests as required; re-run `uv run pytest` until the failing checks pass.

- Coverage requirement: all changes must aim to reach 100% test coverage for the repository. If the repository provides an automated coverage measurement (for example via a pytest plugin), use it; otherwise, add tests to cover all modified code paths and document the coverage reasoning in the change.
- Never ignore or skip failing tests without prior consent: before marking a test as skipped, xfail, or otherwise suppressing a failure, ask the repository owner or requestor for approval and explain the reason and mitigation plan in the same change (e.g., in the PR description or issue).

## Notes for agents

- Do not assume any global tools are available; run the command exactly as shown so the project's environment wrapper (`uv`) provides the correct interpreter and environment.
- When making code changes, include or update tests and then run `uv run pytest` to verify.
- Add any repository-specific test guidance to this file when necessary.
- If an agent believes a failing test should be temporarily suppressed (for example to unblock an urgent fix), the agent must first ask the user for permission, provide the failure details, and include a clear remediation and timeline in the request. Only proceed to suppress after receiving explicit approval.

## Success criteria

- All automated verification of changes must use `uv run pytest` and pass before marking the task complete.

## Post-test verification (subagent)

- After writing tests, running `uv run pytest`, and meeting coverage goals, call the `Explore` subagent to independently verify the new or modified tests.
- The subagent's task: review the test code for completeness and for any "cheats" or shortcuts that invalidate the test (for example: empty assertions, overly broad mocks that bypass behavior, silent xfails, skipped assertions, or tests that only assert internal implementation details rather than observable behavior).
- Provide the subagent with the changed file paths, a short summary of intended behavior, and the command `uv run pytest` output.
- The subagent should produce a short report listing any issues and suggested fixes; address those before finalizing the change.

Checklist for subagent verification:

- Tests exercise all public behaviors and assertions verify outcomes.
- No tests silently skip assertions or mark broad xfails without justification.
- Mocks and monkeypatches do not bypass important code paths without documented rationale.
- External resources are properly isolated or recorded with fixtures.
- Coverage increases are genuine (not from trivial lines) and reach the stated goal.
