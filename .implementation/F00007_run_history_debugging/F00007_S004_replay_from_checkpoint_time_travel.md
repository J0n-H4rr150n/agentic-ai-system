# F00007_S004: Replay from Checkpoint (Time-travel)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow starting a new run from a persisted checkpoint associated with a past run (when available).

## Acceptance Criteria
- Runs in history that include a persisted checkpoint expose that fact via the run history API.
- A client can request replaying a historical run from its persisted checkpoint.
- Replay creates a new run and begins execution without re-running nodes already marked completed in the checkpoint.
- Replay is only available when the history record includes both `workflow_id` and a persisted checkpoint.
- Tests cover the replay API path and ensure the replayed run executes.

## Scope
- Minimal UI addition: provide a replay affordance in the existing Run History panel.
- No new pages.
- No new durable storage layer (still in-memory).

## API
- `POST /api/runs/{run_id}/replay`
  - Starts a new run using the latest graph for the historical run’s `workflow_id`.
  - Seeds execution from the historical record’s persisted checkpoint.

## Tasks
- [x] Create story branch + doc
- [x] Persist checkpoint (when present) into run history records
- [x] Add replay endpoint that launches a new run from a persisted checkpoint
- [x] Add frontend API client support + minimal UI affordance
- [x] Add tests (backend + frontend API client)
- [x] Update feature doc + changelog; mark story complete

## Implementation Notes
- MVP checkpoints exist today only at safe pause/cancel/interrupt boundaries. Replay is therefore available only "where available".

## Files Changed
- `backend/runs/store.py` - Persist optional checkpoint alongside terminal run history records
- `backend/api/routes/run_history.py` - Expose `has_checkpoint` in list and `checkpoint` in detail responses
- `backend/api/routes/run.py` - Persist checkpoint for cancelled runs and add `POST /api/runs/{run_id}/replay`
- `backend/tests/test_run_history_replay.py` - Replay integration test
- `frontend/public/js/api/run-history.js` - Add `replayRun(runId)`
- `frontend/tests/api/run-history.test.js` - Add replayRun test coverage
- `frontend/public/js/ui/run-history.js` - Add per-run Replay button when `has_checkpoint`
- `frontend/public/js/main.js` - Wire replay action and poll live run status/trace
- `frontend/public/css/layout.css` - Styles for Replay button

## Testing
- Backend: `cd backend && python -m pytest -q`
- Frontend: `cd frontend && node --test`

## Blockers / Questions
- None
