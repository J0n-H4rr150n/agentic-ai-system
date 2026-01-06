# F00008_S002: DB-Backed Workflow Persistence

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Persist workflows and their versions to Postgres when `DATABASE_URL` is set, while preserving an in-memory fallback for tests/local runs without DB.

## Tasks
- [x] Implement Postgres-backed workflow store
- [x] Keep in-memory store for fallback
- [x] Ensure nested workflow execution continues to work

## Files Changed
- backend/workflows/store.py
- backend/nodes/control/agent.py
- backend/nodes/control/loop.py

## Testing
- `docker compose run --rm backend pytest -q`

## Notes
- Store selection happens via presence of `DATABASE_URL`.
- Existing workflow API contract preserved.
