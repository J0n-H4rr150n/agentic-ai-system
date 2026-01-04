# F00003_S009: Router Node with Conditions

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a `router` control node that selects a route based on conditions evaluated against the run state.

## Acceptance Criteria
- Multiple output ports based on conditions
- Conditions evaluate against state variables
- Supports: equals, contains, regex, greater_than, less_than
- Default/fallback output port

## Tasks
- [x] Implement `RouterNode` with condition evaluation and deterministic selection
- [x] Add unit tests for matching + default behavior
- [x] Update feature doc + changelog

## Implementation Notes
- The runner currently does not implement conditional edge skipping; this node outputs a selected route so future runner logic (or downstream nodes) can act on it.
- Conditions are evaluated in config order; the first match wins.

## Files Changed
- `backend/nodes/control/router.py`
- `backend/tests/test_nodes_control.py`
- `.implementation/F00003_core_node_library/F00003_S009_router_node_with_conditions.md`
- `.implementation/F00003_core_node_library.md`
- `.implementation/changelog.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None.
