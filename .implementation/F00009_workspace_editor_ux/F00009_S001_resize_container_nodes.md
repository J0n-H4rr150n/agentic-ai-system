# F00009_S001: Resize Container Nodes

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Allow container nodes on the canvas to be resized so users can group workflows at different scales.

## Tasks
- [x] Add resize handle to container rendering when selected
- [x] Add selection interaction to resize via handle drag
- [x] Snap resized dimensions to grid on mouse-up
- [x] Enforce minimum size
- [x] Add unit tests for resize math

## Implementation Notes
- Resizing is anchored to the container’s top-left; drag handle is bottom-right.
- When a container is resized, containment relationships for non-container nodes are recalculated.

## Files Changed
- frontend/public/js/nodes/container.js
- frontend/public/js/selection/index.js
- frontend/public/js/selection/resize-math.js
- frontend/tests/selection/resize-math.test.js

## Testing
- `cd frontend && npm test`
