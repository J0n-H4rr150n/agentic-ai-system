# F00001_S008: Node Selection & Movement

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow users to select nodes (click) and move them (drag) on the canvas.

## Tasks
- [x] Add SelectionManager (hit-test, selection state)
- [x] Implement drag-move using viewport screen→world conversion
- [x] Snap moved nodes to grid on release (10px)
- [x] Add unit tests for hit-testing + drag math

## Implementation Notes
- Pan/zoom remains supported: selection and movement operate in world coordinates.
- Selection uses left click; panning uses middle mouse or space+drag (handled by PanZoomController).
- Hit-testing chooses the topmost node under the cursor and brings it to front when selected.
- Dragging preserves the initial cursor-to-node offset so the node doesn't "jump" when the drag starts.

## Files Changed
- frontend/public/js/selection/index.js (SelectionManager)
- frontend/public/js/selection/move-math.js (pure drag/snap math)
- frontend/public/js/nodes/index.js (hit-testing helpers + bringToFront)
- frontend/public/js/nodes/base.js (selected rendering outline)
- frontend/public/js/canvas/renderer.js (passes selection state to node render)
- frontend/public/js/canvas/index.js (wires SelectionManager into CanvasManager)
- frontend/tests/selection/move-math.test.js (unit tests)
- frontend/tests/nodes/manager.test.js (unit tests)

## Testing
- Manual: `make run`, click a node to select, drag to move, release to snap
- Unit: `npm --prefix frontend test`

## Blockers / Questions
- None.
