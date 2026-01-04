# F00001_S012: Container Detection (Nodes Know Their Parent)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Introduce UI-only container nodes and automatic containment detection so regular nodes can track which container they belong to.

## Acceptance Criteria
- A new `container` node type can be added from the palette.
- When a regular node is moved/dropped inside a container, it records `parentId` equal to that container's node id.
- If a node is moved out of a container, its `parentId` becomes `null`.
- Containers do not interfere with backend execution:
  - `container` nodes are excluded from graph serialization used for run/save.
- Frontend unit tests cover containment detection and serialization behavior.

## Scope
- Minimal container rendering (a labeled rectangle behind other nodes).
- No new pages/modals.
- No backend changes required for execution.

## Tasks
- [x] Create story branch + doc; mark story 🟡 In Progress
- [x] Add container node type + rendering
- [x] Add containment detection (compute parentId)
- [x] Exclude container nodes from graph serialization
- [x] Add frontend unit tests
- [x] Update feature doc + changelog; mark story 🟢 Complete

## Files Changed
- `frontend/public/js/palette/categories.js` - Add Container to palette
- `frontend/public/js/nodes/container.js` - Container node rendering
- `frontend/public/js/nodes/container-math.js` - Containment math helpers
- `frontend/public/js/nodes/base.js` - Add `parentId` metadata
- `frontend/public/js/nodes/index.js` - Container creation + parentId assignment
- `frontend/public/js/selection/index.js` - Update parentId on drop
- `frontend/public/js/graph/serializer.js` - Exclude container nodes from serialization
- `frontend/tests/graph/serializer.test.js` - Verify containers excluded
- `frontend/tests/nodes/container-math.test.js` - Containment math tests
- `frontend/tests/nodes/manager.test.js` - ParentId assignment tests

## Implementation Notes
- Containers are UI-only grouping nodes and are intentionally excluded from serialized graphs so backend execution and node registry validation remain unchanged.

## Testing
- Frontend: `cd frontend && npm test`
- Backend (sanity): `make test-backend-docker`

## Blockers / Questions
- None
