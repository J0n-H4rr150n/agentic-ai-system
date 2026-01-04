# F00002_S005: Base Node Executor Interface

**Status:** 🟡 In Progress
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Define a minimal, testable node execution interface used by the async runner.

## Tasks
- [ ] Add `BaseNode` abstract class defining async `execute()`
- [ ] Add a simple `MockNode` implementation for unit tests
- [ ] Add unit tests for the interface contract

## Implementation Notes
- State container is introduced in S006; this story uses a plain dict-like state input/output.

## Files Changed
- (Fill as implemented)

## Testing
- Unit: `python -m pytest -q backend/tests`

## Blockers / Questions
- None.
