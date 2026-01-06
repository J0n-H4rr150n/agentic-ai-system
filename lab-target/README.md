# lab-target

A safe local HTTP target used to exercise the system’s `browser`, `http_request`, and `http_fuzzer` nodes.

## Endpoints

- `GET /api/health`
- `GET /` (simple HTML page with links + a search form)
- `GET /search?q=...` (echoes query safely)
- `GET /status/{code}` (returns the requested status code)
- `GET /headers` (returns a small subset of request headers)
- `GET /slow?s=...` (adds a small delay)

## Docker Compose

This service is wired into the repo’s `docker-compose.yml` as `lab-target` and exposed at `http://localhost:36303`.
