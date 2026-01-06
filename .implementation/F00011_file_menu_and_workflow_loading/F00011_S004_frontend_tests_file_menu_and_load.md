# F00011_S004: Frontend Tests (File Menu + Load)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Add unit tests to keep the File menu and workflow loading stable.

## Acceptance Criteria

- Tests cover:
  - File menu toggle open/close
  - Load workflow calls `listWorkflows` and `getWorkflow`
  - Graph import into managers happens (clear + add nodes/wires)
  - Export JSON action still serializes the current graph

## Tasks

- [x] Add tests under `frontend/tests/ui/` for file menu controller
- [x] Add tests for load behavior with mocked workflow API
- [x] Add tests for export behavior

## Files Changed

- `frontend/tests/ui/file-menu.test.js` - Added menu toggle/load/export unit tests

## Files (expected)

- `frontend/public/js/ui/file-menu.js` (new)
- `frontend/tests/ui/file-menu.test.js` (new)

## Blockers / Questions

- None.
