# F00007_S002: Run List View (Per Workflow)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a minimal UI to browse past runs for a specific workflow.

## Acceptance Criteria
- Runs can be associated with an optional `workflow_id` when started.
- `GET /api/runs` supports filtering by `workflow_id` (most recent first).
- Frontend shows a run list for the current workflow (the most recently saved workflow id).
- No run detail view is added (that is S003).
- Tests cover backend filter behavior and frontend API/formatting.

## Scope
- Minimal UI embedded in the existing single-page app.
- No new pages or navigation system.

## API
- `GET /api/runs?workflow_id={workflow_id}`

## Tasks
- [x] Create story branch + doc
- [x] Extend run request + persistence with `workflow_id`
- [x] Add backend filtering for run history list
- [x] Add frontend run history API client
- [x] Add minimal run history list UI
- [x] Add tests (backend + frontend)
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/api/routes/run.py` - Accept `workflow_id` and persist into terminal run history records (including resume)
- `backend/api/routes/run_history.py` - Add `workflow_id` filter/query and include field in responses
- `backend/runs/store.py` - Store `workflow_id` and support filtering
- `backend/tests/test_run_history_api.py` - Add filter test
- `frontend/public/index.html` - Add `runHistoryRoot` mount point
- `frontend/public/css/layout.css` - Add run history list styles
- `frontend/public/js/api/run.js` - Send `workflow_id` when provided
- `frontend/public/js/api/run-history.js` - Add run history API client
- `frontend/public/js/ui/run-controls.js` - Pass workflowId into run creation
- `frontend/public/js/ui/run-history.js` - Add per-workflow run list viewer
- `frontend/public/js/main.js` - Wire run history viewer + refresh behavior
- `frontend/tests/api/run.test.js` - Extend tests for workflowId
- `frontend/tests/api/run-history.test.js` - Add tests for run history API client
- `frontend/tests/ui/run-controls.test.js` - Extend tests for workflowId and cancelled formatting
- `frontend/public/js/ui/status.js` - Add cancelled status formatting
- `.implementation/F00007_run_history_debugging.md` - Check off S002
- `.implementation/changelog.md` - Add story entry

## Testing
- `cd backend && poetry run pytest -k "run_history"`
- `cd frontend && node --test`

## Blockers / Questions
- None
