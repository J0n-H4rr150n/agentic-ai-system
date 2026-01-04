# F00001_S009: Port System (Input/Output)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Introduce a minimal, testable Port system so nodes can expose input/output connection points.

## Tasks
- [x] Add `Port` model (input/output) with validation
- [x] Add port layout math (world-space centers)
- [x] Render ports on nodes (respecting pan/zoom)
- [x] Add port hit-testing helpers (for future wiring)
- [x] Add unit tests for port layout + hit-testing

## Implementation Notes
- Ports are world-space primitives attached to nodes.
- Port rendering uses existing node styling (no new theme tokens).
- Default ports per node type:
	- `start`: 1 output
	- `end`: 1 input
	- others: 1 input + 1 output

## Files Changed
- frontend/public/js/nodes/port.js (Port model + layout + hit testing)
- frontend/public/js/nodes/base.js (default ports + rendering)
- frontend/public/js/nodes/index.js (NodeManager port hit-testing)
- frontend/tests/nodes/port.test.js (unit tests)

## Testing
- Unit: `npm --prefix frontend test`
- Manual: `make run` then verify ports render on nodes at left/right edges

## Blockers / Questions
- None.
