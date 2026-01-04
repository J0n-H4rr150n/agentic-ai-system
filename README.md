# Agentive AI System

Visual Agent IDE for building stateful AI agents with a drag-and-drop canvas and a custom state machine runner.

## Quickstart (Docker)

- Run services: `make run`
- Stop services: `make down`
- View logs: `make logs`

Endpoints:
- Frontend: http://localhost:36300
- Backend health: http://localhost:36301/api/health

## Local Backend Testing (Poetry)

The backend uses Poetry for local dependency management and test runs.

1. `cd backend`
2. `poetry install`
3. `poetry run pytest -q`

## Notes

- Docker images install Python dependencies via `pip` using `backend/requirements.txt`.
- If you change backend dependencies, update both `backend/pyproject.toml` (Poetry) and `backend/requirements.txt` (Docker).
