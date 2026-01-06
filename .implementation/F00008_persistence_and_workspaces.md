# F00008: Postgres Persistence + Workspaces

**Status:** 🟢 Complete
**Phase:** 7 (Post-MVP hardening)
**Priority:** P0 (Critical)

## Overview
Add Postgres+pgvector-backed persistence for saved artifacts so workflows and UI workspaces can be saved/loaded across restarts.

This feature also standardizes schema migrations using Alembic, executed automatically on Docker startup.

## Stories
- [x] S001: Add Postgres+pgvector service + Alembic auto-migrations
- [x] S002: DB-backed workflow persistence (with in-memory fallback)
- [x] S003: Workspace persistence API (versioned)

## Acceptance Criteria
- Docker `make run` starts Postgres+pgvector.
- Backend runs `alembic upgrade head` automatically on container start.
- Workflow endpoints persist to Postgres when `DATABASE_URL` is set.
- Workspace endpoints support create/get/list/versioning.
- All backend tests pass in Docker.

## Technical Notes
- Persistence is selected by presence of `DATABASE_URL`.
- Postgres schema managed via Alembic (migration scripts under `backend/alembic/versions/`).
- `vector` extension is created in the initial migration (pgvector available for future RAG concepts).

## Related Files
- backend/alembic.ini
- backend/alembic/
- backend/entrypoint.sh
- backend/workflows/store.py
- backend/workspaces/store.py
- backend/api/routes/workspace.py
- docker-compose.yml
