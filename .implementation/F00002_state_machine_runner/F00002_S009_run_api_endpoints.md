# F00002_S009: Run API Endpoints

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Expose runner execution via HTTP endpoints.

## Tasks
- [x] Add `POST /api/run` that accepts a graph payload and returns a `run_id`
- [x] Add `GET /api/run/{id}` that returns status and trace
- [x] Run execution in the background (asyncio task) with in-memory storage for MVP
- [x] Add unit tests for the endpoints

## Implementation Notes
- MVP uses an in-memory run store (process-local). Persistence/Redis comes later.
- Nodes are executed using minimal built-in no-op node implementations for supported types.

## Files Changed
- backend/main.py
- backend/api/routes/health.py
- backend/api/routes/run.py
- backend/api/__init__.py
- backend/api/routes/__init__.py
- backend/nodes/builtin.py
- backend/tests/test_run_api.py

## Testing
- Unit: `python -m pytest -q backend/tests`

## Blockers / Questions
- None.
