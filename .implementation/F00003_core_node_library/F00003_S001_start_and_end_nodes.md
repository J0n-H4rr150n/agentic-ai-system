# F00003_S001: Start and End Nodes

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Implement the first control-flow nodes for the MVP: `start` and `end`.

## Tasks
- [x] Create `StartNode` implementation
- [x] Create `EndNode` implementation
- [x] Add unit tests
- [x] Wire nodes into run execution (minimal factory)
- [x] Update feature doc + changelog

## Implementation Notes
- The current runner/node interface only passes `state` into `execute()`. To keep Start/End nodes useful without expanding runner scope, both nodes accept a `config` dict at construction time.
- `StartNode` supports `config.initial_state` (dict) and returns it as output so the executor merges it into state.
- `EndNode` returns a snapshot under `config.result_key` (default `result`) and avoids self-referential output by excluding that key from the snapshot.

## Files Changed
- `backend/nodes/control/start.py` - StartNode implementation
- `backend/nodes/control/end.py` - EndNode implementation
- `backend/nodes/control/__init__.py` - control nodes package
- `backend/api/routes/run.py` - instantiate Start/End for their node types
- `backend/tests/test_nodes_control.py` - new unit tests

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- Future story work (S010: registry auto-discovery) should likely centralize type→class mapping instead of the run API building nodes directly.
