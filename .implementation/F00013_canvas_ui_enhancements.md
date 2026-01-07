# F00013: Essential Canvas UI/UX Features

**Status:** 🟢 Phase 1 Complete, Expanded
**Phase:** 9 (Advanced Features)
**Depends on:** F00001 (Canvas Engine), F00009 (Workspace Editor UX)

---

## Overview

Implement professional canvas interaction features similar to Alteryx, Figma, and other visual workflow tools to improve the workflow building experience.

## Completed Stories

### F00013_S001: Container Drag with Children ✅

**Acceptance Criteria:**
- Dragging a container movesall child nodes with it
- Relative positions of children are maintained
- Works smoothly during drag operation
- Parent relationships preserved after drag

**Implementation:**
- Modified `selection/index.js` to detect container drag
- Calculate drag delta and apply to all children
- Filter children by `parentId === container.id`

---

### F00013_S002: Zoom Controls UI ✅

**Acceptance Criteria:**
- Zoom controls appear in bottom-right of canvas
- + button zooms in, - button zooms out
- Percentage display shows current zoom (e.g., "125%")
- Fit button fits all content to screen
- Keyboard shortcuts work (Ctrl+=/-, Ctrl+0, Ctrl+1)

**Implementation:**
- Created `ui/zoom-controls.js` component
- Added zoom functions to `viewport.js`: `zoomIn`, `zoomOut`, `fitToScreen`
- Styled with horizontal floating panel in `canvas.css`
- Integrated into `main.js`

---

### F00013_S003: User-Friendly Workflow Naming ✅

**Acceptance Criteria:**
- Prompt user for workflow name when saving
- Display workflow names in file menu dropdown instead of UUIDs
- Format as "Name (v1)" with version number
- Fall back to UUID if no name provided

**Implementation:**
- Added `prompt()` dialog in `save-as-node.js` before saving
- Modified `createWorkflow` API call to include `name` field
- Updated `file-menu.js` `normalizeWorkflowsResponse` to extract name
- Updated `renderWorkflowOptions` to display name with version

---

### F00013_S004: Node Deletion via Keyboard ✅

**Acceptance Criteria:**
- Delete or Backspace key removes selected node
- Safety check prevents deletion when typing in inputs or textareas
- Selection clears after deletion

**Implementation:**
- Added `removeNode(nodeId)` method to `NodeManager`
- Added `_onKeyDown` event listener in `SelectionManager`
- Check for `isContentEditable`, `HTMLInputElement`, `HTMLTextAreaElement`
- Attached/detached keydown listener in attach/detach methods

---

### F00013_S005: Accurate Node Configuration Schemas ✅

**Acceptance Criteria:**
- All node schemas match actual workflow configs in `sample-workflows.js`
- Start node shows `initial_state.target_url` field
- Browser node has action, url_key, observation_mode, output_key
- LLM node has model select, prompt textarea, json_mode checkbox, output_key
- Router node has output_key, default_output, conditions (JSON array)
- End node has result_key field
- Auto-sync between form fields and Advanced JSON works

**Implementation:**
- Completely rewrote `nodes/schemas.js` based on production usage
- Added nested key support for `initial_state.target_url` in getDefaultConfig
- All node types now have accurate field definitions
- Form field changes auto-update JSON view (already implemented in node-properties.js)

---

## UI Improvements

- Renamed "Save as Node" button to "Save" for clarity
- Fixed zoom percentage color contrast for readability
- All form fields have proper labels, placeholders, and help text

---

## Bug Fixes

### Port Conflict Resolution (Windows Reserved Ports)
- Changed all ports from 36300 range to 10300 range
- Updated `docker-compose.yml`: Frontend 10300, Backend 10301, DB 10302, Lab-target 10303
- Updated `backend/Dockerfile` and `lab-target/Dockerfile` to use new ports
- Application now accessible at http://localhost:10300 (avoids Windows TCP exclusion ranges 36283-36382)

---

## Future Stories

### F00013_S006: Multi-Select
- Drag to draw selection rectangle
- Shift+click to add to selection
- Move multiple nodes together
- Delete multiple nodes with Del key

### F00013_S007: Minimap Overview
- Small overview map in corner
- Shows all nodes as small rectangles
- Current viewport highlighted
- Click/drag to pan

### F00013_S008: Alignment Tools
- Align multiple nodes left/right/top/bottom/center
- Distribute horizontally/vertically
- Match width/height

---

## Files Modified/Created

```
frontend/public/
├── index.html                        [MODIFIED] Renamed Save button
├── css/
│   ├── canvas.css                    [MODIFIED] Zoom controls styling, fixed text color
│   └── layout.css                    [MODIFIED] Form field styling, color contrast fixes
└── js/
    ├── main.js                       [MODIFIED] Initialize zoom controls
    ├── canvas/
    │   └── viewport.js               [MODIFIED] zoomIn, zoomOut, fitToScreen
    ├── nodes/
    │   ├── index.js                  [MODIFIED] Added removeNode method
    │   └── schemas.js                [MODIFIED] Rewrote all schemas to match actual usage
    ├── selection/
    │   └── index.js                  [MODIFIED] Container drag with children, delete key
    └── ui/
        ├── zoom-controls.js          [NEW] Zoom UI component
        ├── save-as-node.js           [MODIFIED] Added name prompt
        └── file-menu.js              [MODIFIED] Display workflow names

docker-compose.yml                    [MODIFIED] All ports to 10300 range
backend/Dockerfile                    [MODIFIED] Port 10301
lab-target/Dockerfile                 [MODIFIED] Port 10303
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + =` or `+` | Zoom in |
| `Ctrl/Cmd + -` | Zoom out |
| `Ctrl/Cmd + 0` | Fit to screen |
| `Ctrl/Cmd + 1` | Reset to 100% |
| `Delete` or `Backspace` | Delete selected node |
| `Ctrl + Wheel` | Zoom (already existed) |
| `Space + Drag` | Pan (already existed) |
| `Middle Mouse Drag` | Pan (already existed) |

---

## Testing Completed

✅ Container drag with children maintains positions
✅ Zoom controls UI functional (buttons + keyboard)
✅ Workflow name prompt and display in dropdown
✅ Node deletion with Delete/Backspace key
✅ Node config forms match actual usage (all node types)
✅ Auto-sync between form fields and JSON
✅ Port changes allow app to run on Windows without conflicts
