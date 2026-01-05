# BUGFIX: Execution Modes Regressions

**Date:** 2026-01-05

## Summary
After introducing run `mode` support (`run`/`test`/`simulate`) a few regressions surfaced when rebuilding and running the backend test suite in Docker.

## Fix
- Make `/api/run` node construction compatible with monkeypatched `build_nodes_for_graph` functions that do not accept a `mode` parameter.
- Fix `simulate` mode guard wrapper so side-effect restrictions are actually enforced.
- Rename internal stub node classes to avoid pytest collecting them as tests.
- Correct new API tests to use the full `GraphDefinition` request shape (matching the real frontend/backend contract).

## Notes
This bugfix restores green backend tests in Docker (`docker compose build backend && docker compose run --rm backend pytest -q`).
