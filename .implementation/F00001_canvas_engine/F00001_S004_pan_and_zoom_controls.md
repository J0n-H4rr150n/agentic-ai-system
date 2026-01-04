# F00001_S004: Pan and Zoom Controls

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add pan and zoom controls to the canvas:
- Pan with middle mouse drag OR space + left-drag
- Zoom with mouse wheel, clamped 25%–400%

## Tasks
- [x] Implement pan/zoom controller and hook it into `CanvasManager`
- [x] Update viewport math to support anchored zoom
- [x] Update grid renderer to respect viewport transforms
- [x] Add unit tests for viewport pan/zoom math

## Implementation Notes
- Keep math pure and unit-testable (no DOM dependencies in core calculations).
- Zoom is anchored at cursor position.

## Files Changed
- `frontend/public/js/canvas/pan-zoom.js` - Pan/zoom controller (middle mouse + space-drag + wheel)
- `frontend/public/js/canvas/viewport.js` - Clamp + pan + anchored zoom helpers
- `frontend/public/js/canvas/grid.js` - Grid respects viewport transforms
- `frontend/public/js/canvas/index.js` - Attach/detach pan/zoom controller
- `frontend/tests/canvas/viewport.test.js` - Unit tests for viewport math

## Testing
- Manual: `make run`, then pan/zoom the canvas
- Unit: `cd frontend && npm test`

## Blockers / Questions
- None.
