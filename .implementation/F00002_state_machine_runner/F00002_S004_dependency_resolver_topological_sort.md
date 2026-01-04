# F00002_S004: Dependency Resolver (Topological Sort)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Compute a deterministic execution order for a graph by resolving dependencies (topological sort).

## Tasks
- [x] Implement topological sort over `ExecutionPlan` adjacency
- [x] Detect cycles and raise a clear error
- [x] Add unit tests for a DAG and for cycle detection

## Implementation Notes
- Deterministic ordering is required for reproducibility and testability.

## Files Changed
- backend/runner/dependency.py
- backend/tests/test_dependency.py

## Testing
- Unit: `python -m pytest -q backend/tests`

## Blockers / Questions
- None.
