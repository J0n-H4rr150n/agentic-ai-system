# F00006_S004: Palette Integration for Saved Agents

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Display saved workflows (“agents”) in the palette so users can discover them from the UI.

## Acceptance Criteria
- Backend exposes an endpoint to list saved workflows.
- Frontend palette displays a “Saved Agents” section populated from the backend.
- Existing built-in palette categories continue to work unchanged.
- Unit tests cover backend listing and frontend palette integration behavior.

## Scope
- Minimal display only; saved agents are not executable as nodes until nested execution (S005).
- Saved agent items are displayed but not draggable to avoid introducing non-executable node types.

## Tasks
- [x] Create story branch + story doc
- [x] Add backend list endpoint for workflows
- [x] Add frontend workflow list API method
- [x] Render “Saved Agents” section in palette
- [x] Add backend + frontend tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/api/routes/workflow.py` - Added workflow list endpoint (`GET /api/workflow`)
- `backend/tests/test_workflow_api.py` - Added test coverage for workflow list
- `frontend/public/js/api/workflow.js` - Added `listWorkflows()`
- `frontend/public/js/main.js` - Loaded workflows and appended a “Saved Agents” palette section
- `frontend/public/js/palette/saved-agents.js` - Pure helper to build palette categories with saved agents
- `frontend/public/js/palette/index.js` - Avoid setting `data-node-type` for display-only items
- `frontend/tests/api/workflow.test.js` - Added `listWorkflows()` unit test
- `frontend/tests/palette/saved-agents.test.js` - Added unit tests for palette category helper
- `.implementation/F00006_fractal_reusable_agents.md` - Checked off S004
- `.implementation/changelog.md` - Added S004 entry

## Implementation Notes
- Saved agents are display-only in this story (items are not draggable) to avoid introducing non-executable node types before nested execution (S005).

## Testing
- `cd backend && poetry run pytest -k workflow`
- `cd frontend && node --test`

## Blockers / Questions
- None
