# F00009: Workspace Editor UX

**Status:** 🟢 Complete
**Phase:** 8
**Priority:** P0 (Critical)

## Overview
Improve the day-to-day usability of the canvas/workspace editor so users can build and maintain workflows effectively.

This feature focuses on UI ergonomics that are required to support real workflows:
- Resizing containers
- Constraining/collapsing the trace viewer so it stays within the browser window
- Editing node properties/config and persisting them via workspace save/load

## Stories
- [x] S001: Resize container nodes
- [x] S002: Trace viewer stays within browser window (collapsible)
- [x] S003: Node properties editor (view/edit/save)
- [x] S004: UI theme (depth + grid/canvas contrast)

## Acceptance Criteria
- Container nodes can be resized via a drag handle.
- Resizing snaps to grid and enforces a minimum size.
- Existing drag/move and wiring interactions continue to work.
- Frontend unit tests remain green.

## Related Files
- frontend/public/js/nodes/container.js
- frontend/public/js/selection/index.js
- frontend/public/js/selection/resize-math.js
- frontend/tests/selection/resize-math.test.js
