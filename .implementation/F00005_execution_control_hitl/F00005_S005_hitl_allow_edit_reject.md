# F00005_S005: Human-in-the-loop Actions (Allow / Edit / Reject)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
When a run reaches an interrupt point, it must pause and await a human decision:
- **Allow**: continue execution deterministically.
- **Edit**: apply a deterministic state edit, then continue.
- **Reject**: stop the run in a terminal state.

## Acceptance Criteria
- Runs pause automatically on `interrupt.before` and/or `interrupt.after` for configured nodes.
- While paused for an interrupt, `GET /api/run/{id}` exposes pending interrupt metadata (node id, phase, reason).
- `POST /api/run/{id}/hitl/allow` resumes execution.
- `POST /api/run/{id}/hitl/edit` applies a validated `state_patch` into checkpoint state and resumes.
- `POST /api/run/{id}/hitl/reject` transitions the run to a terminal state.
- Tests cover pause → allow/edit/reject behavior.

## Scope (This Story)
- Backend-only HITL control.
- State edits are limited to applying a JSON object patch into checkpoint state.

## Tasks
- [x] Implement interrupt-triggered pause in executor/run control flow
- [x] Add pending interrupt metadata to run record + API responses
- [x] Add HITL decision endpoints (allow/edit/reject)
- [x] Add integration tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/runner/executor.py` - Pause on interrupt points and carry handled interrupt keys
- `backend/api/routes/run.py` - Pending interrupt metadata and HITL endpoints (allow/edit/reject)
- `backend/models/run.py` - Persist handled interrupt keys in RunCheckpoint
- `backend/tests/test_run_hitl.py` - Integration tests for HITL flows
- `.implementation/F00005_execution_control_hitl.md` - Marked S005 complete
- `.implementation/changelog.md` - Added S005 changelog entry

## Testing
- `cd backend && python -m pytest -q`

## Blockers / Questions
- None
