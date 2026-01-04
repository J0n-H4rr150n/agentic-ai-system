# F00006_S002: “Save as Node” Action (Frontend)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow the user to save the current graph to the backend as a reusable workflow/agent.

## Acceptance Criteria
- UI exposes a “Save as Node” action.
- Clicking it sends the current serialized graph to `POST /api/workflow`.
- UI displays the returned `workflow_id`.
- Frontend unit tests cover API client and controller behavior.

## Scope
- Minimal toolbar action only (no palette integration or versioning).

## Tasks
- [x] Add workflow API client module (frontend)
- [x] Add “Save as Node” toolbar action and status display
- [x] Add frontend tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `frontend/public/index.html` - Added “Save as Node” button and workflow status display
- `frontend/public/js/main.js` - Wired save controller into toolbar
- `frontend/public/js/api/workflow.js` - Added workflow create/get API client
- `frontend/public/js/ui/save-as-node.js` - Added save-as-node controller
- `frontend/public/js/ui/workflow-status.js` - Added workflow save status formatter/indicator
- `frontend/tests/api/workflow.test.js` - Added API unit tests
- `frontend/tests/ui/save-as-node.test.js` - Added controller unit tests
- `frontend/tests/ui/workflow-status.test.js` - Added workflow status formatting unit tests

## Implementation Notes
- Reused existing API client conventions (`/api` baseUrl + relative paths like `/workflow`).
- Kept UX minimal: toolbar button triggers save; status line shows returned `workflow_id`.

## Testing
- `cd frontend && node --test`

## Blockers / Questions
- None
