# F00003_S013: Loop Control Node

**Status:** 🟢 Complete
**Phase:** 3 (Core Node Library)
**Priority:** P0 (Critical)

## Goal

Add a `loop` control node that iterates a saved workflow (subgraph) until a break condition is met (or a max iteration limit is reached).

This must fit the current runner constraints (DAG execution): the loop happens *inside* the node by repeatedly executing a referenced workflow.

## Requirements

- Node type: `loop`
- Config:
  - `workflow_id` (string, required): saved workflow to execute.
  - `version` (int, optional): workflow version to load (default: latest).
  - `max_iterations` (int, optional, default: 10): maximum loop iterations.
  - `break_key` (string, required): dotted state path; loop stops when this value becomes truthy after an iteration.
  - `iteration_key` (string, optional, default: `loop_iteration`): state key written before each iteration with a 1-based iteration number.
  - `output_key` (string, optional, default: `loop_output`): root key to write loop summary.
- Output:
  - Merges final nested state mapping into the parent state (same behavior pattern as `agent`).
  - Adds `__loop__` metadata including at least: `workflow_id`, `version`, `iterations`, `stopped_reason`, `break_value`.
  - Adds `{output_key: {...}}` summary with the same information.
- Must respect execution modes:
  - When the parent run mode is `test`/`simulate`, the loop’s nested node construction must use the same mode.

## Acceptance Criteria

- [ ] `loop` node can execute a child workflow multiple times and stops when `break_key` becomes truthy.
- [ ] `loop` node stops at `max_iterations` when the break condition is never met.
- [ ] Node is available via registry discovery and can be constructed by the node factory.
- [ ] Schema inference understands `loop` similarly to `agent` (best-effort nested merge).
- [ ] Frontend palette lists `Loop` under Control.
- [ ] Tests cover the happy path and max-iterations path.

## Implementation Notes

- The executor and graph parser do not support cyclic graphs yet; do not introduce cycles.
- Reuse the existing nested workflow execution pattern used by `agent`.

## Files Changed

- backend/nodes/control/loop.py
- backend/nodes/control/agent.py
- backend/runner/node_factory.py
- backend/workflows/schema.py
- frontend/public/js/palette/categories.js
- backend/tests/test_run_loop_node.py
- backend/tests/test_node_registry.py
- backend/tests/test_workflow_schema_api.py
