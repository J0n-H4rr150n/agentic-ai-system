# F00002_S001: FastAPI Project Setup & Docker

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Stand up the backend service skeleton so it can be run via Docker Compose and exercised with automated tests.

## Tasks
- [x] Create `backend/` scaffold with FastAPI entrypoint
- [x] Add `/api/health` endpoint
- [x] Add Dockerfile using pip installs via `requirements.txt`
- [x] Add minimal pytest coverage for health endpoint
- [x] Add Poetry config for local dev/testing (Docker continues using pip)

## Implementation Notes
- App creation is exposed as `create_app()` for testability.
- Docker sets `PYTHONPATH=/app` so `pytest` can import local modules without extra flags.

## Files Changed
- `backend/main.py` - FastAPI app factory + `/api/health`
- `backend/requirements.txt` - pip dependencies for Docker
- `backend/pyproject.toml` - Poetry dependencies for local dev/tests
- `backend/Dockerfile` - pip install + copy source + PYTHONPATH
- `backend/tests/test_health.py` - health endpoint test

## Testing
- Docker: `make test-backend-docker`
- Local: `cd backend && poetry install && poetry run pytest -q`

## Blockers / Questions
- None.
