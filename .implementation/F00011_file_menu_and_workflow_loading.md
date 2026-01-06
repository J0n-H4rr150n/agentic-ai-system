# F00011: File Menu + Workflow Loading (UI)

**Status:** 🟢 Complete
**Phase:** 2
**Priority:** P1 (High)
**Target:** 2026-01-06

## Overview

Add a slim, clean top bar “File” menu system and a first-class way to load a saved workflow into the canvas.

This must:
- Use existing backend endpoints (`GET /api/workflow`, `GET /api/workflow/{id}`).
- Use existing graph import wiring (`loadGraphIntoManagers`) and existing canvas managers.
- Avoid inventing new pages/flows; keep it minimal and consistent with current UI.

## Stories

- [x] S001: Slim Top Bar + File Menu UI Shell
- [x] S002: Load Workflow Into Canvas (from `/api/workflow`)
- [x] S003: Move Export JSON Into File Menu
- [x] S004: Frontend Tests (File Menu + Load)

## Acceptance Criteria

- A “File” menu exists in the top bar.
- The menu supports “Load workflow…” which:
  - Lists saved workflows (id + latest version)
  - On selection, fetches the workflow and replaces the current canvas graph
  - Stores current workflow id in `localStorage` (re-using existing key)
- “Export JSON” remains available via the menu.
- Tests cover:
  - Rendering/menu interactions
  - Successful import calls into `loadGraphIntoManagers`

## Related Files

- `frontend/public/index.html`
- `frontend/public/css/layout.css`
- `frontend/public/js/main.js`
- `frontend/public/js/api/workflow.js`
- `frontend/public/js/graph/sample-workflows.js` (import helper)
- `frontend/tests/ui/`
