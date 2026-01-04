# F00005_S004: Force-stop Mechanism (Cancel Run)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow a running (or paused) run to be force-stopped so it transitions to a terminal state and stops further execution.

## Acceptance Criteria
- Backend exposes a cancel endpoint for runs.
- Cancelling a running run causes it to stop at a safe boundary and transition to a terminal `cancelled` state.
- Cancelling is idempotent.
- Trace up to the cancel point is preserved.
- Tests cover cancel behavior.

## Scope (This Story)
- Backend-only cancel control.
- UI wiring is handled later.

## Tasks
- [x] Review current run execution + pause/resume control flow
- [x] Add terminal `cancelled` status and API response updates
- [x] Add `POST /api/run/{run_id}/cancel` endpoint
- [x] Update executor/run loop to honor cancel requests at safe boundaries
- [x] Add backend integration tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/runner/executor.py` - Added cancel callback support and `RunCancelled` exception
- `backend/api/routes/run.py` - Added cancel endpoint, run status, and executor wiring
- `backend/tests/test_run_pause.py` - Added cancel integration tests
- `.implementation/F00005_execution_control_hitl.md` - Marked S004 complete
- `.implementation/changelog.md` - Added S004 changelog entry

## Testing
- `cd backend && python -m pytest -q`

## Blockers / Questions
- None
