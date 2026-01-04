# F00005_S006: Runtime Control Channel (WebSocket)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Provide a bidirectional runtime control channel over WebSocket so the UI can send control actions (pause/resume/cancel/HITL decisions) without relying on one-off HTTP requests.

> SSE remains the mechanism for step streaming; the WebSocket is for control and immediate status responses.

## Acceptance Criteria
- Backend exposes a WebSocket endpoint for run control.
- Client can send JSON commands to: pause, resume, cancel, HITL allow, HITL edit, HITL reject.
- Server responds with current run status (and interrupt metadata when relevant).
- Invalid commands receive a structured error response (no server crash).
- Tests cover WebSocket control behavior.

## Scope
- Backend-only control channel.
- No frontend wiring in this story.

## Tasks
- [x] Add WebSocket control endpoint
- [x] Reuse existing control logic (no duplicated state transitions)
- [x] Add integration tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/api/routes/run.py` - Added `WS /api/run/{id}/control` and shared helpers
- `backend/tests/test_run_ws_control.py` - WebSocket control integration tests
- `.implementation/F00005_execution_control_hitl.md` - Marked S006 complete
- `.implementation/changelog.md` - Added S006 changelog entry

## Testing
- `cd backend && python -m pytest -q`

## Blockers / Questions
- None
