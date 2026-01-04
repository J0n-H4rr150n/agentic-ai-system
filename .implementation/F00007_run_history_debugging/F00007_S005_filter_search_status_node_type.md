# F00007_S005: Filter/Search (Status + Node Type)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow narrowing the Run History list by terminal status and by node type involved in the run.

## Acceptance Criteria
- Run History list supports filtering by terminal status (`completed`, `failed`, `cancelled`).
- Run History list supports filtering by node type (derived from the graph executed for the run).
- Filters do not add any new pages; stays within the existing Run History panel.
- Backend supports these filters via query params and is covered by tests.
- Frontend has unit tests verifying the API client query params.

## Scope
- Minimal UI controls (simple selects) within Run History.
- No full-text search beyond these filters.

## API
- `GET /api/runs?workflow_id=...&status=...&node_type=...`

## Tasks
- [x] Create story branch + doc
- [x] Persist node-id→type mapping into run history records
- [x] Add `status` + `node_type` filters to `/api/runs`
- [x] Add minimal filter controls to Run History UI
- [x] Add tests (backend + frontend)
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/runs/store.py` - Persist node-id→type mapping; filter list by status/node_type
- `backend/api/routes/run_history.py` - Accept `status`/`node_type` query params on `GET /api/runs`
- `backend/api/routes/run.py` - Persist node-id→type mapping when terminalizing a run
- `backend/tests/test_run_history_filters.py` - API coverage for status/node_type filtering
- `frontend/public/js/api/run-history.js` - Add `status` + `nodeType` params to `listRuns`
- `frontend/tests/api/run-history.test.js` - Verify query params for filters
- `frontend/public/js/ui/run-history.js` - Add status select + node type input
- `frontend/public/css/layout.css` - Style run history filter controls
- `backend/Dockerfile` - Ensure Docker image preserves `backend.*` package layout
- `.implementation/F00007_run_history_debugging.md` - Mark S005 complete
- `.implementation/F00007_run_history_debugging/F00007_S005_filter_search_status_node_type.md` - Story status/tasks/files

## Implementation Notes
- Node type filtering uses a persisted node-id→type mapping captured from the executed graph, so filtering does not require re-fetching workflow graphs.
- Docker backend image now copies sources into `/app/backend` so imports like `backend.api.routes.*` work consistently (and `make test-backend-docker` can run).

## Testing
- Backend: `make test-backend-docker`
- Frontend: `cd frontend && npm test`

## Blockers / Questions
- None
