# F00002_S002: Pydantic Models for Graph Schema

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Define Pydantic v2 models for the graph schema exchanged between the frontend and backend.

## Tasks
- [x] Add `GraphDefinition`, `NodeDefinition`, `EdgeDefinition` models
- [x] Validate IDs, required fields, and basic referential integrity (edge endpoints reference existing nodes)
- [x] Add unit tests for happy path + invalid graphs

## Implementation Notes
- Models align with the frontend export format (`{version,nodes,edges}`) and include node `position`, `size`, `ports`, and `config`.

## Files Changed
- backend/models/graph.py
- backend/models/__init__.py
- backend/__init__.py
- backend/tests/test_models_graph.py
- backend/tests/test_health.py (import path fix)

## Testing
- Unit: `python -m pytest -q backend/tests`

## Blockers / Questions
- None.
