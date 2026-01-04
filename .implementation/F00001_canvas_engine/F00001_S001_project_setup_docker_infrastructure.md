# F00001_S001: Project Setup & Docker Infrastructure

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Create the minimal runnable project skeleton for the Visual Agent IDE MVP so that:
- `docker compose up` starts both frontend (Node.js/Express) and backend (FastAPI)
- Frontend serves a static page from `frontend/public/`
- Backend exposes an `/api/health` endpoint

This story focuses on infrastructure and scaffolding only (no canvas behavior yet).

## Tasks
- [x] Create root `docker-compose.yml`
- [x] Add root `Makefile` with `make run` helpers
- [x] Frontend scaffold: `frontend/` with Express server, Dockerfile, and static `public/index.html`
- [x] Backend scaffold: `backend/` with FastAPI app, Dockerfile, and basic routing
- [x] Add minimal automated tests (backend health endpoint)
- [x] Document how to run locally (README update if needed)
- [x] Add Poetry config for local backend testing

## Implementation Notes
- Follow folder structure from `.planning/plan.md` (Phase 1 MVP).
- Keep files small (<200 lines) and testable.
- Use dependency injection patterns early (even if mocked).

## Files Changed
- `docker-compose.yml` - Starts `frontend` and `backend`
- `Makefile` - Standardized `make run`/`make down` workflow
- `README.md` - Quickstart + Poetry local test guidance
- `frontend/server.js` - Minimal Express server + `/health`
- `frontend/package.json` - Express dependency and start script
- `frontend/Dockerfile` - Container image build
- `frontend/public/index.html` - Static scaffold page
- `backend/main.py` - FastAPI app factory + `/api/health`
- `backend/requirements.txt` - pip dependencies for Docker
- `backend/pyproject.toml` - Poetry config for local dev/testing
- `backend/Dockerfile` - pip install + copy source + PYTHONPATH
- `backend/tests/test_health.py` - health endpoint test

## Testing
- `make run`
- `curl http://localhost:36300` returns HTML
- `curl http://localhost:36301/api/health` returns JSON ok
- Local: `cd backend && poetry run pytest`
- Docker: `make test-backend-docker`

## Blockers / Questions
- None yet.
