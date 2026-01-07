# F00013_S003: User-Friendly Workflow Naming

**Status:** 🟢 Complete
**Feature:** F00013 Canvas UI Enhancements
**Completed:** 2026-01-07

## Objective

Allow users to give workflows friendly names instead of only seeing UUIDs, making it easier to identify saved workflows.

## Acceptance Criteria

- [x] Prompt user for workflow name when clicking Save
- [x] Display workflow names in file menu dropdown instead of UUIDs
- [x] Format as "Name (v1)" with version number
- [x] Fall back to UUID if no name provided

## Implementation

### Files Modified

- `frontend/public/js/ui/save-as-node.js` - Added name prompt
- `frontend/public/js/ui/file-menu.js` - Display names in dropdown
- `frontend/public/index.html` - Renamed button from "Save as Node" to "Save"

### Technical Details

**Save Prompt:**
```javascript
const name = prompt("Enter a name for this workflow:", "My Workflow");
if (!name || !name.trim()) {
  return; // User cancelled
}

const created = await workflowApi.createWorkflow({
  graph,
  name: name.trim()
});
```

**Display Logic:**
```javascript
function normalizeWorkflowsResponse(result) {
  return workflows.map((w) => ({
    workflowId: w.workflow_id,
    name: w.name || null, // Extract name
    latestVersion: w.latest_version
  }));
}

function renderWorkflowOptions({ workflows }) {
  const displayName = wf.name || wf.workflowId;
  const version = wf.latestVersion ? ` (v${wf.latestVersion})` : "";
  opt.textContent = `${displayName}${version}`;
}
```

## Testing

✅ Click Save → prompt appears
✅ Enter name → workflow saved with name
✅ File menu shows "My Workflow (v1)"
✅ Cancel prompt → save cancelled
✅ Empty name → save cancelled
✅ No name provided → falls back to UUID
