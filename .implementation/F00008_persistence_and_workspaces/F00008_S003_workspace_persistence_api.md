# F00008_S003: Workspace Persistence API

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Add an API to save/load/list versioned "workspace" documents (UI state) with Postgres persistence when available.

## Tasks
- [x] Add workspace store (in-memory + Postgres-backed)
- [x] Add workspace API routes: create/get/list/versioning
- [x] Add tests matching workflow API style

## API
- `POST /api/workspace` → create workspace
- `GET /api/workspace` → list workspaces
- `GET /api/workspace/{workspace_id}` → get latest or `?version=`
- `POST /api/workspace/{workspace_id}/version` → create version
- `GET /api/workspace/{workspace_id}/versions` → list versions

## Files Changed
- backend/workspaces/store.py
- backend/api/routes/workspace.py
- backend/main.py
- backend/tests/test_workspace_api.py

## Testing
- `docker compose run --rm backend pytest -q`
