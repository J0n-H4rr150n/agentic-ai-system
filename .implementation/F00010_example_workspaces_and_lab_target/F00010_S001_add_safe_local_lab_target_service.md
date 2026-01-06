# F00010_S001: Add Safe Local Lab Target Service

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Provide a safe, predictable local HTTP service to test the `browser`, `http_request`, and `http_fuzzer` nodes against, without relying on external sites or intentionally vulnerable targets.

## Acceptance Criteria

- Service is included in `docker-compose.yml` as `lab-target`.
- Exposed on host port `36303` (port policy compliant).
- Provides stable endpoints used by example workflows:
  - `GET /` (simple HTML)
  - `GET /api/health`
  - `GET /search?q=...`
  - `GET /status/{code}`
  - `GET /headers`
  - `GET /slow?s=...`
- Basic unit tests exist for the service.
- A smoke test is documented and confirmed working (`curl http://localhost:36303/api/health`).

## Tasks

- [x] Scaffold `lab-target/` FastAPI app
- [x] Add `lab-target` Dockerfile + requirements
- [x] Wire service into `docker-compose.yml`
- [x] Add basic unit tests for endpoints
- [x] Confirm container serves `/api/health` reliably (fix if needed)
- [x] Update changelog after story completion

## Implementation Notes

- This target is intentionally safe: it escapes/normalizes echoed input.
- If `curl` fails but the container is running, check container logs and port binding.

## Files Changed

- `docker-compose.yml` — added `lab-target` service on `36303`
- `lab-target/Dockerfile` — container build/run
- `lab-target/requirements.txt` — FastAPI + uvicorn
- `lab-target/app/main.py` — endpoints
- `lab-target/tests/test_app.py` — unit tests
- `lab-target/README.md` — endpoint documentation

## Testing

- Build + start: `docker compose up --build -d lab-target`
- Smoke test: `curl http://localhost:36303/api/health`

## Blockers / Questions

- Previously: host `curl` to `http://localhost:36303/api/health` returned exit code 52; re-checked and confirmed `200 OK`.
