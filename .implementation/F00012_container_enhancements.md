# F00012: Container Parent-Child Enhancements

**Status:** S001 & S002 Complete, In Progress
**Phase:** Phase 9 (Advanced Features)
**Depends on:** F00001 (Canvas Engine), F00009 (Workspace Editor UX)

---

## Overview

Implement Alteryx-style container functionality for visual organization and selective execution of workflow nodes. Containers act as visual grouping elements with parent-child relationships, enabling better organization of complex workflows.

---

## Stories

### F00012_S001: Parent-Child Relationship Display ✅ Complete

**Acceptance Criteria:**
- Node properties panel shows parent container (if any)
- Container properties panel shows list of child nodes
- Container title displays child count (e.g., "Container (3)")
- Parent updates automatically when nodes are moved

**Technical Notes:**
- Parent tracking already exists via `updateParentForNode()`
- Enhance `node-properties.js` to display parent/children
- Update `container.js` render to show child count
- Hook into drag-drop to update parent on move

---

### F00012_S002: Visual Container Enhancements ✅ Complete

**Acceptance Criteria:**
- Containers render with semi-transparent background
- Clear visual distinction between containers and nodes
- Highlight container when child node is selected
- Different visual states for empty vs. populated containers

**Technical Notes:**
- Update `container.js` rendering
- Add CSS classes for container states
- Consider color coding or border styles

---

### F00012_S003: Collapse/Expand Containers (Future)

**Acceptance Criteria:**
- Container header has collapse/expand button
- Collapsed containers hide child nodes
- Collapsed containers show abbreviated child list
- State persists during session

**Technical Notes:**
- Add collapsed state to container model
- Filter nodes during render based on parent's collapsed state
- Update serialization to preserve state

---

### F00012_S004: Selective Container Execution (Future)

**Acceptance Criteria:**
- "Run Container" button in container properties
- Execute only nodes within selected container
- Trace viewer shows container-scoped execution
- Container boundaries maintained during execution

**Technical Notes:**
- Backend: Add `container_id` filter to executor
- Frontend: Add run button to container properties
- Update trace viewer to highlight container scope

---

## Folder Structure

```
frontend/public/js/
├── ui/
│   └── node-properties.js       # [MODIFIED] Add parent/children display
├── nodes/
│   ├── container.js              # [MODIFIED] Add child count to title
│   ├── index.js                  # [MODIFIED] Ensure parent updates on move
│   └── container-math.js         # [EXISTS] Container bounds detection
└── canvas/
    └── drag.js                   # [MODIFIED] Update parent after drag
```

---

## API Specifications

No new API endpoints required for Phase 1.

Future: `POST /api/run/container/{container_id}`

---

## UI/UX Mockup

### Node Properties (when node is selected)
```
┌─────────────────────────────┐
│ Node Properties             │
├─────────────────────────────┤
│ Node ID: start-1            │
│ Type: start                 │
│ Title: [Start Node        ] │
│ Parent: Container 1         │ ← NEW
│ Config (JSON):              │
│ {...}                       │
└─────────────────────────────┘
```

### Container Properties (when container selected)
```
┌─────────────────────────────┐
│ Container Properties        │
├─────────────────────────────┤
│ Node ID: container-1        │
│ Type: container             │
│ Title: [My Container      ] │
│ Children (3):               │ ← NEW
│   • start-1 (start)         │
│   • browser-1 (browser)     │
│   • llm-1 (llm)             │
│ [Run Container]             │ ← FUTURE
└─────────────────────────────┘
```

---

## Testing Plan

### Manual Verification
1. Drag container onto canvas
2. Drag multiple nodes into container
3. Select node → verify parent shows in properties
4. Select container → verify children list appears
5. Move node out of container → verify parent clears
6. Resize container → verify parent updates correctly

### Browser Testing
- Use browser tool to verify all property displays
- Test nested containers (if supported)
- Verify child count in container title

---

## Notes

- Inspired by Alteryx container functionality
- Containers already render behind nodes (via `unshift`)
- Parent tracking logic exists, just needs UI exposure
- Future stories will add collapse/expand and selective execution
