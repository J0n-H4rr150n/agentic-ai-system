# F00013_S009: Delete Node Button and Clear Canvas

**Status:** 🟢 Complete
**Feature:** F00013 Canvas UI Enhancements
**Completed:** 2026-01-07

## Objective

Add UI buttons for deleting nodes and clearing the entire canvas, with confirmation dialogs to prevent accidental data loss.

## Acceptance Criteria

- [x] "Delete Node" button in properties panel
- [x] Confirmation dialog before deleting node
- [x] "Clear" button in zoom controls next to Fit button
- [x] Confirmation modal before clearing canvas
- [x] Red/danger styling for destructive actions

## Implementation

### Delete Node Button (Properties Panel)

**Files Modified:**
- `frontend/public/js/ui/node-properties.js`
- `frontend/public/css/layout.css`

**Features:**
- Button appears in properties actions row alongside Save button
- Disabled when no node is selected
- Shows confirmation dialog with node title/ID
- Clears selection after deletion

**Code:**
```javascript
const deleteButton = el("button", "properties-delete");
deleteButton.type = "button";
deleteButton.textContent = "Delete Node";

deleteButton.addEventListener("click", () => {
  if (!selectedNodeId) return;

  const node = nodeManager.getById(selectedNodeId);
  if (!node) {
    loadNode(null);
    return;
  }

  if (confirm(`Delete node "${node.title ||node.id}"?`)) {
    nodeManager.removeNode(selectedNodeId);
    loadNode(null);
  }
});
```

**CSS Styling:**
```css
.properties-delete {
  padding: 8px 12px;
  border: 1px solid #dc2626;
  border-radius: 8px;
  background: #dc2626;
  color: #ffffff;
  cursor: pointer;
  font-size: 11px;
}

.properties-delete:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}
```

### Clear Canvas Button (Zoom Controls)

**Files Modified:**
- `frontend/public/js/ui/zoom-controls.js`
- `frontend/public/css/canvas.css`

**Features:**
- Button appears after Fit button in zoom controls
- Danger variant styling (red)
- Multi-line confirmation modal
- Removes all nodes from canvas

**Code:**
```javascript
const clearBtn = document.createElement("button");
clearBtn.className = "zoom-control-button zoom-control-button--wide zoom-control-button--danger";
clearBtn.textContent = "Clear";
clearBtn.title = "Clear all nodes from canvas";
clearBtn.type = "button";

clearBtn.addEventListener("click", () => {
  if (confirm("Clear all nodes from the canvas?\n\nThis cannot be undone.")) {
    const nodes = [...canvasManager.nodeManager.getNodes()];
    nodes.forEach(node => canvasManager.nodeManager.removeNode(node.id));
  }
});
```

**CSS Styling:**
```css
.zoom-control-button--danger {
  background: #dc2626;
  color: #ffffff;
  border-color: #dc2626;
}

.zoom-control-button--danger:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}
```

## User Experience

**Delete Node Button:**
1. User selects a node
2. Properties panel shows node details
3. User clicks "Delete Node" (red button)
4. Confirmation dialog: "Delete node \"Start Node\"?"
5. If confirmed, node is removed and selection clears

**Clear Button:**
1. User has nodes on canvas
2. User clicks "Clear" button (red, next to Fit)
3. Confirmation modal: "Clear all nodes from the canvas?\n\nThis cannot be undone."
4. If confirmed, all nodes are removed

## Design Decisions

**Red Color (#dc2626):**
- Standard danger/destructive action color
- Matches common UI conventions (GitHub, Tailwind, etc.)
- Darker shade on hover (#b91c1c) provides feedback

**Confirmation Dialogs:**
- Native `confirm()` for simplicity and consistency
- Multi-line text for Clear button emphasizes severity
- Shows node title/ID for Delete button for clarity

**Button Placement:**
- Delete button in properties panel (context-specific)
- Clear button in zoom controls (global canvas action)
- Both logically grouped with related actions

## Testing

✅ Delete button disabled when no selection
✅ Delete button enabled when node selected
✅ Confirmation shows correct node name
✅ Canceling confirmation keeps node
✅ Confirming deletes node and clears selection
✅ Clear button shows confirmation
✅ Canceling clear keeps all nodes
✅ Confirming clear removes all nodes
✅ Red styling clearly indicates danger

## Future Enhancements

- Custom modal instead of native `confirm()` for better styling
- Undo/redo support to recover from accidental deletion
- Multi-select delete (delete multiple nodes at once)
- Export before clear option
