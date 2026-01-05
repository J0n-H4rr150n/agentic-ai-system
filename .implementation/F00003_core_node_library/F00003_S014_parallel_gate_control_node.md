# F00003_S014: Parallel Gate Control Node

**Status:** 🟢 Complete
**Phase:** 3 (Core Node Library)
**Priority:** P0 (Critical)

## Goal

Add a `parallel_gate` control node used to model explicit fork/join structure in graphs.

The current runner already executes independent nodes concurrently; this node provides a first-class, validated primitive for:
- **fork**: a clear fan-out boundary
- **join**: a clear fan-in boundary

## Requirements

- Node type: `parallel_gate`
- Config:
  - `gate` (string, optional, default: `join`): one of `fork`, `join`.
  - `fanout` (int, optional): required when `gate=fork`; must be >= 2.
  - `output_key` (string, optional, default: `parallel_gate_output`).
- Output:
  - Writes `{output_key: {...}}` with at least: `gate`, `fanout` (if applicable).

## Acceptance Criteria

- [ ] `parallel_gate` node executes as a no-op boundary (does not mutate state except its own output).
- [ ] `fork` validates `fanout`.
- [ ] Node is available via registry discovery and can be constructed by the node factory.
- [ ] Schema inference includes `output_key` as an output.
- [ ] Frontend palette lists `Parallel Gate` under Control.
- [ ] Tests cover validation and a fork/parallel/join run topology.

## Implementation Notes

- Do not change runner semantics in this story.
- Fork/join behavior is represented structurally via edges; join is enforced by multiple incoming edges.

## Files Changed

- backend/nodes/control/parallel_gate.py
- backend/runner/node_factory.py
- backend/workflows/schema.py
- frontend/public/js/palette/categories.js
- backend/tests/test_nodes_control.py
- backend/tests/test_run_parallel_gate_node.py
- backend/tests/test_node_registry.py
- backend/tests/test_workflow_schema_api.py
