# F00005_S001: Interrupt Point Configuration on Nodes

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Introduce a first-class, validated way to mark nodes as interrupt points (human-in-the-loop) so later stories can pause execution and await an Allow/Edit/Reject decision.

## Acceptance Criteria
- Graph JSON supports specifying interrupt configuration per-node.
- Backend validates interrupt configuration (rejects invalid shapes / conflicting settings).
- Interrupt configuration is available to the runner/executor layer (even if pausing behavior is implemented in later stories).
- Unit tests cover valid and invalid configurations.

## Proposed Schema (MVP)
Each node may include an optional `interrupt` object:

```json
{
  "interrupt": {
    "before": true,
    "after": false,
    "reason": "Optional human-readable string"
  }
}
```

Rules:
- At least one of `before`/`after` must be true.
- `reason` is optional, max length 280.

## Tasks
- [x] Identify the correct backend model(s) to extend for per-node config
- [x] Add interrupt config schema + validation
- [x] Ensure it flows through parse/execute layers
- [x] Add unit tests
- [x] Update feature doc + changelog; mark story complete

## Implementation Notes
- This story only adds configuration + validation + plumbing. Actual pause/resume is implemented in later stories.

## Files Changed
- `backend/models/graph.py` - Add `InterruptConfig` and `NodeDefinition.interrupt`
- `backend/runner/graph_parser.py` - Plumb interrupts into `ExecutionPlan`
- `backend/tests/test_models_graph.py` - Add interrupt validation tests
- `backend/tests/test_graph_parser.py` - Assert interrupt plumbing
- `.planning/plan.md` - Mark completed phases and update next steps
- `.implementation/F00005_execution_control_hitl.md` - Update story checklist
- `.implementation/changelog.md` - Add story entry
- `.implementation/F00005_execution_control_hitl/F00005_S001_interrupt_point_configuration.md` - Story doc

## Testing
- `cd backend && python -m pytest -q`

## Blockers / Questions
- None
