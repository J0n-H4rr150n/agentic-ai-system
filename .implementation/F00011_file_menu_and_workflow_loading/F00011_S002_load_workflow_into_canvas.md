# F00011_S002: Load Workflow Into Canvas (from `/api/workflow`)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Add a “Load workflow…” action that fetches saved workflows and imports the selected graph into the canvas.

## Acceptance Criteria

- Menu action “Load workflow…” lists workflows from `GET /api/workflow`.
- Selecting an item fetches the workflow graph via `GET /api/workflow/{workflow_id}`.
- Graph is imported into the active canvas (`nodeManager` + `wireManager`) using existing import logic.
- The selected workflow id is stored in `localStorage` under `currentWorkflowId` (existing key).

## Tasks

- [x] Create loader UI (minimal: native `<select>` or small inline list inside menu)
- [x] Call `workflowApi.listWorkflows()` and render results
- [x] On select, call `workflowApi.getWorkflow(workflowId)`
- [x] Import graph into canvas managers
- [x] Clear trace viewer + reset statuses appropriately (minimal)

## Implementation Notes

- Uses `workflowApi.listWorkflows()` on menu open to populate a `<select>`.
- Uses `workflowApi.getWorkflow(workflowId)` and imports the returned graph via `loadGraphIntoManagers`.
- Clears trace viewer and resets run status to idle before importing.
- Stores workflow id under `localStorage.currentWorkflowId` and updates run history filtering.

## Files Changed

- `frontend/public/js/main.js` - Wired load behavior into menu + localStorage
- `frontend/public/js/ui/file-menu.js` - Added async refresh + load handlers

## Files (expected)

- `frontend/public/js/main.js`
- `frontend/public/js/ui/file-menu.js` (new)
- `frontend/public/js/graph/sample-workflows.js` (reuse `loadGraphIntoManagers`)

## Testing

- Mock `workflowApi` to return a workflow list + graph.
- Assert import is called and managers are cleared/populated.

## Blockers / Questions

- None.
