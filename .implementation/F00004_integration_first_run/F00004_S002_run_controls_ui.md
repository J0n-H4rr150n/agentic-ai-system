# F00004_S002: Run Controls UI (Run button, status indicator)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a minimal toolbar with a Run button and a status indicator so users can execute the current canvas graph against the backend runner.

## Acceptance Criteria
- UI shows a Run button in a toolbar
- Clicking Run serializes the current graph and POSTs it to `/api/run`
- Status indicator shows: idle, running, completed, failed
- Unit tests cover the run-control logic

## Tasks
- [x] Add toolbar markup (Run button + status)
- [x] Add run-control controller logic (calls Run API + polls)
- [x] Add unit tests
- [x] Update feature doc + changelog

## Implementation Notes
- This story uses polling (`GET /api/run/{id}`) until the run is no longer `running`.
- SSE updates are handled in F00004_S003.

## Files Changed
- `frontend/public/index.html`
- `frontend/public/css/layout.css`
- `frontend/public/js/ui/status.js`
- `frontend/public/js/ui/run-controls.js`
- `frontend/public/js/main.js`
- `frontend/tests/ui/run-controls.test.js`
- `.implementation/F00004_integration_first_run/F00004_S002_run_controls_ui.md`
- `.implementation/F00004_integration_first_run.md`
- `.implementation/changelog.md`

## Testing
- `cd frontend && npm test`

## Blockers / Questions
- None
