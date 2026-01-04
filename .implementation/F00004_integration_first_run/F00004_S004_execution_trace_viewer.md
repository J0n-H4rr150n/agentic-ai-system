# F00004_S004: Execution Trace Viewer (GitHub Actions style)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a trace viewer panel that renders step traces in real time.

## Acceptance Criteria
- Panel shows a list of steps (collapsible)
- Each step shows: node name, type, status icon, duration
- Expanding a step shows input, output, and error (if any)
- If a step output contains a browser screenshot (base64), show an image preview
- Auto-scroll to the most recent step while running

## Tasks
- [x] Add trace viewer markup container
- [x] Add trace viewer modules (`ui/trace/*`)
- [x] Wire SSE step events to the trace viewer
- [x] Add unit tests for trace formatting/sanitization
- [x] Update feature doc + changelog

## Implementation Notes
- Node name/type are sourced from the submitted graph (node id/title/type); the backend step trace only includes `node_id`.
- Large base64 fields are sanitized in JSON displays while still showing an image preview.

- Trace viewer listens to SSE `step` events emitted by `/api/run/{id}/stream`.
- The viewer auto-scrolls to the newest step while steps append.

## Files Changed
- `frontend/public/index.html`
- `frontend/public/js/ui/run-controls.js`
- `frontend/public/js/ui/trace/detail.js`
- `frontend/public/js/ui/trace/index.js`
- `frontend/public/js/ui/trace/step.js`
- `frontend/public/js/main.js`
- `frontend/tests/ui/trace-format.test.js`
- `.implementation/F00004_integration_first_run/F00004_S004_execution_trace_viewer.md`
- `.implementation/F00004_integration_first_run.md`
- `.implementation/changelog.md`

## Testing
- `cd frontend && npm test`
- `cd backend && pytest`

## Blockers / Questions
- None
