# F00007_S003: Run Detail View (Steps, Inputs/Outputs, Screenshots)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow reopening a past run and viewing its step-by-step trace (including inputs/outputs and screenshots) beyond the live trace viewer.

## Acceptance Criteria
- Clicking a run in the Run History list loads that run’s details.
- The trace viewer renders the loaded run steps with the same detail UI as live runs (inputs/outputs/errors/screenshot).
- If the run has a `workflow_id`, the workflow graph is loaded so node titles/types can be shown in the trace viewer.
- No replay/checkpoint functionality is added (that is S004).
- Tests cover run history detail API client and selection-to-load behavior.

## Scope
- Reuse the existing single-page UI.
- Reuse the existing trace viewer components (no new pages).

## API
- `GET /api/runs/{run_id}` (existing)
- `GET /api/workflow/{workflow_id}` (existing; used to load graph metadata)

## Tasks
- [x] Create story branch + doc
- [x] Add run history detail API client (`getRun`)
- [x] Make run history list selectable and load detail on click
- [x] Load workflow graph (when available) to enrich trace viewer
- [x] Add tests (frontend)
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `frontend/public/js/api/run-history.js` - Added `getRun(runId)` for fetching persisted run details
- `frontend/public/js/ui/run-history-loader.js` - DOM-free loader that fetches run detail + (optional) workflow graph
- `frontend/public/js/ui/run-history.js` - Made run rows clickable with an `onRunSelected(runId)` callback
- `frontend/public/js/main.js` - Wired run selection to populate the trace viewer from persisted history
- `frontend/public/css/layout.css` - Added hover/cursor affordance for clickable run items
- `frontend/tests/api/run-history.test.js` - Added `getRun(...)` API client test
- `frontend/tests/ui/run-history-loader.test.js` - Added loader unit tests

## Testing
- Frontend: `cd frontend && node --test`
- Backend (unchanged in this story): `cd backend && poetry run pytest`

## Blockers / Questions
- None
