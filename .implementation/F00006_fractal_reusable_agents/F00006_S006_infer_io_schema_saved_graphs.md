# F00006_S006: Infer Input/Output Schema from Saved Graphs

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Infer a simple input/output schema for a saved workflow graph so it can be treated like a reusable component.

## Acceptance Criteria
- Backend can infer a best-effort list of state keys that a workflow *reads* (inputs) and *writes* (outputs).
- A new endpoint returns the inferred schema for a saved workflow id (and optional version).
- Schema inference is deterministic and covered by backend tests.

## Scope
- Backend-only.
- Best-effort inference based on node types/config (no dynamic execution or LLM-based analysis).

## API
- `GET /api/workflow/{workflow_id}/schema?version=`
  - Returns `{ workflow_id, version, inputs, outputs, warnings }`.

## Tasks
- [x] Create schema inference module under `backend/workflows/`
- [x] Add workflow schema endpoint under `backend/api/routes/workflow.py`
- [x] Add backend tests for schema inference endpoint
- [x] Update feature doc + changelog; mark story complete

## Implementation Notes
- Prefer conservative inference:
  - `inputs`: keys referenced by node configs (e.g., router condition keys, prompt keys).
  - `outputs`: keys the node is known to write (e.g., end result key, explicit configured output keys).
- Include `warnings` for unsupported node types or configs that can’t be statically analyzed.

## Files Changed
- `backend/workflows/schema.py` - Best-effort workflow input/output schema inference
- `backend/api/routes/workflow.py` - Added `GET /api/workflow/{workflow_id}/schema`
- `backend/tests/test_workflow_schema_api.py` - Tests for schema inference endpoint

## Testing
- `cd backend && poetry run pytest -q -k "workflow_schema"`

## Blockers / Questions
- None
