# F00006_S005: Nested Execution (Agent-within-Agent)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow a saved workflow to be executed as a single node inside another graph.

## Acceptance Criteria
- A new node type can reference a saved `workflow_id` (and optional version).
- When executed, the node loads the referenced workflow graph and runs it as a subgraph.
- The subgraph runs with the parent state as its initial state.
- The node output merges the subgraph’s final state into the parent.
- Parent trace includes an execution boundary containing the child trace payload.
- Backend tests cover a simple nested execution flow end-to-end via the run API.

## Scope
- Backend-only execution support (no frontend drag/drop or palette changes in this story).
- Nested trace is included inside the parent step output as a JSON payload.

## Tasks
- [x] Create story branch + story doc
- [x] Implement Agent node that runs a referenced workflow graph
- [x] Wire node registry + factory support for the new node type
- [x] Add tests validating nested execution and trace payload
- [x] Update feature doc + changelog; mark story complete

## Implementation Notes
- Implemented `agent` node type (`AgentNode`) that loads a saved workflow graph by `workflow_id` and optional `version`.
- Subgraph execution uses parent state as initial state and returns the subgraph final state merged back into the parent.
- Nested trace boundary is returned under reserved output key `__agent__` including `{workflow_id, version, trace}`.
- Avoided circular imports by importing `build_nodes_for_graph` inside `AgentNode.execute()`.

## Files Changed
- `backend/workflows/store.py` - Shared in-memory workflow store used by API routes and node execution
- `backend/workflows/__init__.py` - Package marker
- `backend/api/routes/workflow.py` - Refactored to use the shared workflow store
- `backend/nodes/control/agent.py` - New `AgentNode` implementation
- `backend/runner/node_factory.py` - Factory support for `agent` node type
- `backend/tests/test_run_nested_agent.py` - End-to-end nested execution test via run API

## Testing
- `cd backend && poetry run pytest -k "workflow or run"`

## Blockers / Questions
- None
