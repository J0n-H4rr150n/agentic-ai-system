# F00003_S010: Node Registry & Auto-Discovery

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Replace the MVP hardcoded node-type allowlist with a real `NodeRegistry` that can:
- register node types
- list available node types
- auto-discover node modules under `backend.nodes.*`

This supports graph validation and future UI features (palette population).

## Acceptance Criteria
- `NodeRegistry` supports `register`, `get`, `list_all`, `is_supported`
- Auto-discovery imports modules and registers exported node types
- Runner graph parsing validates against the registry (no stale allowlist)
- Unit tests cover discovery + supported types

## Tasks
- [x] Implement registry + auto-discovery
- [x] Add module exports for discovery
- [x] Wire into graph parser
- [x] Add tests
- [x] Update feature doc + changelog

## Implementation Notes
- Implemented a `NodeRegistry` with one-time `discover()` that imports modules under `backend.nodes.*`.
- Discovery uses module-level exports: `NODE_TYPE` (string) and `NODE_CLASS` (BaseNode subclass).
- `parse_graph(...)` now validates node types by ensuring the registry has discovered and supports each node.

## Files Changed
- `backend/nodes/registry.py`
- `backend/runner/graph_parser.py`
- `backend/nodes/control/start.py`
- `backend/nodes/control/end.py`
- `backend/nodes/control/router.py`
- `backend/nodes/browser/node.py`
- `backend/nodes/http/request.py`
- `backend/nodes/llm/base.py`
- `backend/tests/test_node_registry.py`
- `.implementation/F00003_core_node_library/F00003_S010_node_registry_auto_discovery.md`
- `.implementation/F00003_core_node_library.md`
- `.implementation/changelog.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None.
