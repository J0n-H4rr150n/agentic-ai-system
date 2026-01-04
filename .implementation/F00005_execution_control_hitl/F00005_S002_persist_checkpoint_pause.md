# F00005_S002: Persist Checkpoint + Pause Execution

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add the ability to request a pause for an in-flight run and persist a checkpoint at a safe boundary so the run can be resumed in a later story.

## Acceptance Criteria
- Backend exposes a pause control endpoint for a run.
- When pause is requested during execution, the run transitions to a paused terminal-ish state and a checkpoint is persisted.
- Checkpoint contains enough information to resume execution deterministically later (state snapshot + completed nodes + any needed scheduler metadata).
- Unit/integration tests cover pause behavior and checkpoint persistence.

## Scope (This Story)
- Backend-only pause + checkpoint persistence.
- Resume behavior is implemented in F00005_S003.

## Tasks
- [x] Review current run store and executor to choose pause/checkpoint integration point
- [x] Add checkpoint model + store (initially in-memory)
- [x] Add `POST /api/run/{run_id}/pause` endpoint
- [x] Update executor to stop at safe boundary when pause requested
- [x] Add backend tests
- [x] Update feature doc + changelog; mark story complete

## Implementation Notes
- MVP safe boundary: between executor batches (after applying deterministic results), so state is consistent.
- If pause is requested, executor completes current batch then persists checkpoint and stops.

## Files Changed
- `backend/models/run.py` - Add `RunCheckpoint`
- `backend/runner/executor.py` - Add pause callback + `RunPaused` checkpoint exception
- `backend/api/routes/run.py` - Add pause + checkpoint endpoints and paused run status
- `backend/tests/test_run_pause.py` - Integration test for pause/checkpoint
- `.implementation/F00005_execution_control_hitl.md` - Update story checklist
- `.implementation/changelog.md` - Add story entry
- `.implementation/F00005_execution_control_hitl/F00005_S002_persist_checkpoint_pause.md` - Story doc

## Testing
- `cd backend && python -m pytest -q`

## Blockers / Questions
- None
