# F00008_S001: Postgres+pgvector + Alembic Auto-Migrations

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Add a Postgres+pgvector database to Docker Compose and ensure Alembic migrations run automatically whenever Docker services are rebuilt/started.

## Tasks
- [x] Add Postgres+pgvector service to `docker-compose.yml`
- [x] Add SQLAlchemy/Alembic/psycopg/pgvector dependencies (Poetry + Docker)
- [x] Add Alembic scaffolding + initial migration
- [x] Add backend entrypoint to wait for DB + run migrations before starting

## Files Changed
- docker-compose.yml
- backend/requirements.txt
- backend/pyproject.toml
- backend/Dockerfile
- backend/entrypoint.sh
- backend/alembic.ini
- backend/alembic/env.py
- backend/alembic/script.py.mako
- backend/alembic/versions/0001_init_workflows_and_workspaces.py
- backend/db/base.py
- backend/db/engine.py
- backend/db/models.py

## Testing
- `docker compose up -d db`
- `docker compose run --rm backend pytest -q`

## Notes
- Postgres is exposed on host port `36302` (within the repo port policy).
- Migrations use `DATABASE_URL` and are invoked automatically by the backend container entrypoint.
