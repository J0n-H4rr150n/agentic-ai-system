# F00002_S012: Execution Modes (Validate/Test/Simulate/Run)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Implement the Phase 2 execution modes described in `.planning/plan.md`:
- **Validate**: check graph structure/dependencies/type compatibility without executing.
- **Test**: execute using mocked node outputs.
- **Simulate**: dry-run using real read-only actions only (no side effects).
- **Run**: full execution (current behavior).

## Tasks
- [x] Add `POST /api/validate` endpoint that validates a graph without running it
- [x] Wire `mode` into execution so `test` and `simulate` behave differently from `run`
- [x] Add tests for validate endpoint and mode behavior
- [x] Update docs and changelog; check plan checkbox

## Implementation Notes
- Keep changes minimal and mode behavior explicit.
- For **simulate** we conservatively block side-effecting actions:
	- `http_request`: only allows `GET|HEAD|OPTIONS`
	- `browser`: only allows `navigate` (blocks `click`/`type`)
- For **test** we use deterministic stub nodes for external I/O nodes (`http_request`, `browser`) so runs are hermetic.

## Files Changed
- `backend/api/routes/run.py` - pass `mode` into node factory
- `backend/api/routes/validate.py` - new validation endpoint
- `backend/main.py` - register validate router
- `backend/runner/node_factory.py` - mode-aware node construction
- `backend/runner/mode_guard.py` - simulate-mode validators
- `backend/runner/test_doubles.py` - test-mode stub nodes
- `backend/tests/test_validate_api.py` - validate endpoint tests
- `backend/tests/test_run_modes.py` - test/simulate behavior tests

## Testing
- `make test-backend-docker`

## Blockers / Questions
- Confirm whether simulate should allow outbound GET requests (currently planned as “real calls but no side effects”).
