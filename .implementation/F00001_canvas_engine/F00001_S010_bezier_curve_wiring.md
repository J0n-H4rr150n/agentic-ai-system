# F00001_S010: Bezier Curve Wiring

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Allow users to wire node ports together by click-drag, with wires rendered as smooth bezier curves on the canvas.

## Tasks
- [x] Add bezier math utilities (pure functions) + unit tests
- [x] Add `Wire` + `WireManager` for storing connections
- [x] Render wires as cubic beziers (viewport-aware)
- [x] Add wiring interaction: click output port → drag preview → release on input port creates wire
- [x] Ensure selection/dragging doesn’t interfere with port wiring

## Implementation Notes
- Wires connect **output → input** only.
- Rendering is canvas-based and respects viewport pan/zoom.

## Files Changed
- frontend/public/js/wires/bezier.js (bezier math)
- frontend/public/js/wires/wire.js (Wire model)
- frontend/public/js/wires/index.js (WireManager)
- frontend/public/js/wires/interaction.js (click-drag wiring)
- frontend/public/js/canvas/renderer.js (wire rendering + preview)
- frontend/public/js/canvas/index.js (wire manager + interaction wiring)
- frontend/public/js/selection/index.js (ignore port clicks)
- frontend/tests/wires/bezier.test.js (unit tests)
- frontend/tests/wires/manager.test.js (unit tests)

## Testing
- Unit: `npm --prefix frontend test`
- Manual: `make run` then drag from an output port to an input port and verify a curved wire appears

## Blockers / Questions
- None.
