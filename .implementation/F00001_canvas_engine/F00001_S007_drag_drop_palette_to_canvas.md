# F00001_S007: Drag-Drop from Palette to Canvas

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow users to drag a node type from the palette onto the canvas.

Acceptance criteria for this story:
- Nodes can be dragged from palette onto canvas
- Nodes snap to the grid when placed (10px)

## Tasks
- [x] Implement palette drag handler
- [x] Convert drop point (screen) → world coords via viewport
- [x] Snap placed nodes to 10px grid
- [x] Add unit tests for drop/snap math

## Implementation Notes
- Dragging creates a temporary “ghost” button; dropping over the canvas creates a new node.
- Placement uses world coordinates; top-left is snapped to grid.

## Files Changed
- `frontend/public/js/palette/drag.js` - Palette drag/drop handler + ghost
- `frontend/public/js/palette/drop-math.js` - Pure drop + snap math
- `frontend/public/js/palette/categories.js` - Added `getPaletteTitleForType()` helper
- `frontend/public/js/main.js` - Wired drag/drop handler into app init
- `frontend/public/js/nodes/index.js` - Added `addFromPalette()` helper
- `frontend/public/js/utils/id.js` - Lightweight ID generator
- `frontend/public/css/layout.css` - Drag ghost styling
- `frontend/tests/palette/drop-math.test.js` - Drop/snap unit tests

## Testing
- Manual: `make run` then drag any palette item onto the canvas
- Unit: `cd frontend && npm test`

## Blockers / Questions
- None.
