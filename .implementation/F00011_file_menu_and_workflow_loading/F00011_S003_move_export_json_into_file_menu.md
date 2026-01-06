# F00011_S003: Move Export JSON Into File Menu

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Move the existing “Export JSON” action into the new File menu so the left palette stays focused on nodes/tools.

## Acceptance Criteria

- “Export JSON” no longer appears as a standalone button in the left sidebar.
- “Export JSON” is available under File menu.
- Export behavior is unchanged.

## Tasks

- [x] Remove `#exportJsonButton` from sidebar markup
- [x] Add File menu item “Export JSON”
- [x] Wire menu item to existing graph serialization + download

## Files Changed

- `frontend/public/index.html` - Removed sidebar Export JSON button, added menu item
- `frontend/public/js/main.js` - Reused existing serialization + download logic from File menu

## Files (expected)

- `frontend/public/index.html`
- `frontend/public/js/main.js`

## Testing

- Test that triggering “Export JSON” invokes download helper with stringified graph.

## Blockers / Questions

- None.
