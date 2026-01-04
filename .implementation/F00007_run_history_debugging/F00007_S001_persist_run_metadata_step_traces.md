# F00007_S001: Persist Run Metadata + Step Traces

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Persist run metadata and step traces so completed runs can be reopened later.

## Acceptance Criteria
- Completed/failed/cancelled runs are persisted in a run-history store after execution.
- Persisted record includes: run_id, status, started_at, completed_at, error (if any), and full step trace.
- A new API endpoint lists persisted runs (most-recent first).
- A new API endpoint fetches a persisted run by id.
- Backend tests cover persistence + API behavior.

## Scope
- Backend-only persistence (in-memory store is OK for this story).
- No UI changes in this story.

## API
- `GET /api/runs` → list persisted runs
- `GET /api/runs/{run_id}` → fetch persisted run detail

## Tasks
- [x] Add run history store module
- [x] Wire persistence into run lifecycle
- [x] Add run history API endpoints
- [x] Add backend tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/runs/store.py` - Add in-memory store for terminal run records
- `backend/api/routes/run_history.py` - Add list/detail endpoints for persisted runs
- `backend/api/routes/run.py` - Persist terminal run records on completion/failure/cancel
- `backend/main.py` - Register run history router
- `backend/tests/test_run_history_api.py` - Add API + persistence test
- `.implementation/F00007_run_history_debugging.md` - Check off S001
- `.implementation/changelog.md` - Add story entry

## Testing
- `cd backend && poetry run pytest -k "run_history"`
- `cd backend && poetry run pytest`

## Blockers / Questions
- None
