# F00003_S008: HTTP Request Node

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add an `http_request` node that can make outbound HTTP calls for the MVP workflow.

## Acceptance Criteria
- Supports GET, POST, PUT, DELETE, PATCH
- Supports custom headers
- Supports JSON body and form body
- Captures response: status, headers, body

## Tasks
- [x] Implement `HTTPRequestNode` using `httpx` (async) with dependency injection
- [x] Add unit tests using `httpx.MockTransport`
- [x] Update feature doc + changelog

## Implementation Notes
- The current runner/node contract is `async execute(state: dict) -> dict`, so config is passed at construction time.
- Prefer injectable `httpx.AsyncClient` (or transport) to avoid real network calls in tests.

## Files Changed
- `backend/nodes/http/__init__.py`
- `backend/nodes/http/request.py`
- `backend/tests/test_nodes_http_request.py`
- `.implementation/F00003_core_node_library/F00003_S008_http_request_node.md`
- `.implementation/F00003_core_node_library.md`
- `.implementation/changelog.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None.
