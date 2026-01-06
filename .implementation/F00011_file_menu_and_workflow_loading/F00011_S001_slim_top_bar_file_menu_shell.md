# F00011_S001: Slim Top Bar + File Menu UI Shell

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Introduce a simple “File” menu in the top toolbar without expanding the UI surface area beyond what’s needed.

## Acceptance Criteria

- Toolbar includes a “File” dropdown/menu trigger.
- Menu can be opened/closed via click.
- Menu is visually slim/clean and consistent with existing CSS variables/tokens.

## Tasks

- [x] Add markup hooks to `index.html`
- [x] Add minimal JS controller for toggling menu open/closed
- [x] Add minimal CSS styling using existing theme tokens

## Implementation Notes

- Added a minimal toolbar dropdown using existing CSS tokens and a small controller module.
- Kept the menu surface area to the required actions only.

## Files Changed

- `frontend/public/index.html` - Added File menu markup in toolbar
- `frontend/public/css/layout.css` - Added minimal File menu styling
- `frontend/public/js/ui/file-menu.js` - New menu controller

## Files (expected)

- `frontend/public/index.html`
- `frontend/public/css/layout.css`
- `frontend/public/js/ui/file-menu.js` (new)

## Testing

- Unit test for menu open/close behavior.

## Blockers / Questions

- None.
