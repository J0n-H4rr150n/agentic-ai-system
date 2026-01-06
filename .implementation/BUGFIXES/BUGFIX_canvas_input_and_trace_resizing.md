# BUGFIX: Canvas Input + Trace Resizing

**Status:** 🟢 Complete
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Summary
Fix several usability issues in the canvas editor:
- Trace viewer stayed constrained during browser resize (no drifting off-screen).
- Mouse wheel scroll behaves normally; canvas zoom happens only on Ctrl+mousewheel.
- Standard canvas panning works via click+drag on empty background.
- Spacebar no longer scrolls the page.

## Changes
- Trace viewer/container sizing:
  - Ensure nested grid containers can shrink correctly using `min-height: 0`.
  - Allow trace body to flex to fill its available height.

- Input behavior:
  - Wheel zoom gated behind `Ctrl`.
  - Spacebar prevented from triggering page scroll when not typing.
  - Space+drag panning intercepts before node/wire mouse handlers.
  - Background drag panning added via `SelectionManager` when clicking empty space.

## Files Changed
- frontend/public/css/layout.css
- frontend/public/js/canvas/pan-zoom.js
- frontend/public/js/selection/index.js

## Testing
- `cd frontend && npm test`
