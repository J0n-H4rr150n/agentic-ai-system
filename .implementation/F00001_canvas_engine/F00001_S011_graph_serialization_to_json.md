# F00001_S011: Graph Serialization to JSON

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Export the current canvas graph (nodes + edges) to a JSON file suitable for backend execution.

## Tasks
- [x] Add graph serializer module (pure)
- [x] Include nodes, edges, positions, configs in JSON
- [x] Add minimal UI action ("Export JSON")
- [x] Add unit tests for serialization

## Implementation Notes
- Keep serialization deterministic (stable ordering) for testability.
- UI export downloads a `graph.json` file (no new pages/modals).

## Files Changed
- frontend/public/js/graph/serializer.js (pure serialization)
- frontend/public/js/main.js (Export JSON button handler + download)
- frontend/public/index.html (Export JSON button)
- frontend/public/js/nodes/base.js (node config support)
- frontend/tests/graph/serializer.test.js (unit tests)

## Testing
- Unit: `npm --prefix frontend test`
- Manual: `make run` then click "Export JSON" and inspect downloaded JSON

## Blockers / Questions
- None.
