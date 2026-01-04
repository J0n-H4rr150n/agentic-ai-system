# F00001_S005: Base Node Class & Rendering

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Introduce a reusable, testable node primitive and render it onto the canvas.

## Tasks
- [x] Add `BaseNode` class (world coordinates, bounds, hit-test)
- [x] Add `NodeManager` to track nodes
- [x] Render nodes in the main render loop (after grid)
- [x] Add unit tests for node geometry/hit-testing

## Implementation Notes
- Use world coordinates for node positions; renderer converts to screen via viewport.
- Keep node logic testable by separating geometry helpers.

## Files Changed
- `frontend/public/js/nodes/base.js` - Base node primitive and renderer
- `frontend/public/js/nodes/index.js` - NodeManager + demo node
- `frontend/public/js/utils/geometry.js` - Geometry helpers
- `frontend/public/js/canvas/renderer.js` - Render nodes after grid
- `frontend/public/js/canvas/index.js` - Inject NodeManager into renderer
- `frontend/tests/utils/geometry.test.js` - Geometry unit tests
- `frontend/tests/nodes/base.test.js` - Node hit-test unit tests

## Testing
- Manual: `make run` and confirm a demo node is visible and moves with pan/zoom
- Unit: `cd frontend && npm test`

## Blockers / Questions
- None.
