# F00009_S002: Trace Viewer Stays Within Window (Collapsible)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Ensure the trace viewer always stays within the browser window and can be collapsed/expanded to reclaim canvas space.

## Tasks
- [x] Add Collapse/Expand toggle button in Trace Viewer header
- [x] Make trace viewer height controlled by CSS variable in the workspace layout
- [x] Ensure trace content scrolls within its panel (no page overflow)
- [x] Add unit test for collapse class toggling

## Implementation Notes
- Collapsing toggles a single CSS class on the `.workspace` element (`workspace--trace-collapsed`).
- When collapsed, the trace viewer body is hidden and the trace row height shrinks.

## Files Changed
- frontend/public/index.html
- frontend/public/css/layout.css
- frontend/public/js/main.js
- frontend/public/js/ui/trace/collapse.js
- frontend/tests/ui/trace-collapse.test.js
- .implementation/F00009_workspace_editor_ux.md

## Testing
- `cd frontend && npm test`
