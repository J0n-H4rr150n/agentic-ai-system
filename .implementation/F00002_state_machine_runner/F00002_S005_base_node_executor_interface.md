# F00002_S005: Base Node Executor Interface

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Define a minimal, testable node execution interface used by the async runner.

## Tasks
- [x] Add `BaseNode` abstract class defining async `execute()`
- [x] Add a simple `MockNode` implementation for unit tests
- [x] Add unit tests for the interface contract

## Implementation Notes
- State container is introduced in S006; this story uses a plain dict-like state input/output.

## Files Changed
- backend/nodes/base.py
- backend/nodes/mock.py
- backend/tests/test_nodes_base.py

## Testing
- Unit: `python -m pytest -q backend/tests`

## Blockers / Questions
- None.
