# F00004_S006: End-to-End Test Against Local Lab

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Verify end-to-end execution against a local lab target with trace visibility.

## Context
Local lab is running at: `http://localhost:47658/`

## Acceptance Criteria
- Running the sample workflow produces step traces end-to-end
- The trace viewer renders step output including a screenshot preview (when available)
- Provide a repeatable verification path:
  - automated integration test against a local in-process HTTP server
  - manual steps for running against the real local lab URL

## Tasks
- [x] Create backend node factory that can instantiate built-in nodes (start/end/router/http_request/browser/llm)
- [x] Provide a minimal browser implementation usable in tests (HTTP fetch + HTML + dummy screenshot)
- [x] Add backend integration test that runs a graph against a local test server
- [x] Update the sample workflow default target URL to `http://localhost:47658/`
- [x] Ensure trace viewer screenshot extraction handles nested outputs (e.g., `{"browser_output": {"screenshot": ...}}`)
- [x] Update feature doc + changelog

## Implementation Notes
- Keep Playwright optional: the E2E test uses a lightweight HTTP-backed page implementation.
- If running via Docker Compose, `localhost` inside the backend container will not reach the host lab; use `host.docker.internal` manually if needed.

## Files Changed
- `backend/runner/node_factory.py`
- `backend/nodes/browser/httpx_page.py`
- `backend/nodes/llm/fake_client.py`
- `backend/api/routes/run.py`
- `backend/tests/test_e2e_local_server_run.py`
- `frontend/public/js/graph/sample-workflows.js`
- `frontend/public/js/ui/trace/detail.js`
- `frontend/tests/ui/trace-format.test.js`
- `.implementation/F00004_integration_first_run/F00004_S006_end_to_end_test_against_local_lab.md`
- `.implementation/F00004_integration_first_run.md`
- `.implementation/changelog.md`

## Testing
- `cd backend && pytest`
- `cd frontend && npm test`

## Manual Verification
1. Ensure lab is running at `http://localhost:47658/`
2. Start the system (local or Docker): `make run`
3. Open frontend: `http://localhost:36300`
4. Confirm the sample graph is present
5. Click Run
6. Verify trace viewer shows steps and screenshot preview for the browser step

## Blockers / Questions
- None
