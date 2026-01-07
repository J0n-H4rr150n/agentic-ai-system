# F00014_S003: Human Approval Node

**Status:** � Complete
**Feature:** F00014 Autonomous Agent Nodes
**Started:** 2026-01-07
**Completed:** 2026-01-07

## Objective

Create a `human_approval` node that pauses workflow execution and waits for human approval/rejection, enabling safe autonomous agent workflows where critical decisions require oversight.

## Acceptance Criteria

- [x] `human_approval` node type added to schemas
- [x] Configurable title and message
- [x] Configurable state keys to display for context
- [x] Timeout with auto-rejection
- [x] Two output ports: "approved" and "rejected"
- [x] Backend pauses workflow execution
- [x] Frontend UI for approval/rejection

## Use Cases

1. **Low Confidence Actions** - LLM confidence < 0.5 requires human review
2. **High Risk Operations** - Delete, modify, or execute critical actions
3. **Cost Checkpoints** - Expensive API calls need approval
4. **Learning Mode** - Review all agent decisions during training
5. **Compliance** - Required human oversight for regulated actions

## Implementation

### Frontend Schema

**File:** `frontend/public/js/nodes/schemas.js`

```javascript
human_approval: {
    fields: [
        {
            key: 'title',
            label: 'Approval Title',
            type: 'text',
            placeholder: 'Review Proposed Action',
            default: 'Human Approval Required',
            required: true,
            help: 'Title shown in approval prompt'
        },
        {
            key: 'message',
            label: 'Message',
            type: 'textarea',
            placeholder: 'The agent wants to perform the following action...',
            rows: 3,
            required: true,
            help: 'Explanation of what needs approval'
        },
        {
            key: 'show_state_keys',
            label: 'State Keys to Display (JSON Array)',
            type: 'textarea',
            placeholder: '["llm_action", "llm_confidence", "llm_reasoning"]',
            rows: 2,
            help: 'Which state values to show for context (JSON array of strings)'
        },
        {
            key: 'timeout_seconds',
            label: 'Timeout (seconds)',
            type: 'number',
            default: 300,
            min: 10,
            max: 3600,
            help: 'Auto-reject after this many seconds'
        }
    ]
}
```

### Example Workflow Usage

```
[LLM Node] → outputs: confidence=0.45, action="delete_user"
     ↓
[Router] → check if confidence < 0.5
     ↓ (yes)
[Human Approval]
  title: "Review Low Confidence Action"
  message: "Agent wants to delete user with low confidence"
  show_state_keys: ["llm_action", "llm_confidence", "llm_reasoning"]
     ↓
  ┌─────────────┬─────────────┐
  │  Approved   │  Rejected   │
  └──────┬──────┴──────┬──────┘
         ↓             ↓
    [Execute]      [Log & End]
```

### Approval UI Mockup

```
┌────────────────────────────────────────┐
│ Review Low Confidence Action           │
├────────────────────────────────────────┤
│ Agent wants to delete user with low    │
│ confidence.                            │
│                                        │
│ Context:                               │
│ • Action: delete_user                  │
│ • Confidence: 0.45                     │
│ • Reasoning: User appears inactive but │
│   data is ambiguous                    │
│                                        │
│ Auto-rejects in: 4:32                  │
│                                        │
│     [Approve] [Reject]                 │
└────────────────────────────────────────┘
```

### Backend Implementation

**File:** `backend/runner/nodes/human_approval.py` (NEW)

```python
"""
Human approval node executor.
Pauses workflow and waits for human approval.
"""

import asyncio
import json
from typing import Dict, Any, Callable


class ApprovalTimeoutError(Exception):
    """Raised when approval times out."""
    pass


async def execute_human_approval_node(
    node_config: Dict[str, Any],
    state: Dict[str, Any],
    approval_callback: Callable
) -> Dict[str, Any]:
    """
    Execute human approval node.

    Args:
        node_config: Node configuration
        state: Current workflow state
        approval_callback: Async function to request approval

    Returns:
        Execution result with routing decision
    """
    title = node_config.get('title', 'Human Approval Required')
    message = node_config.get('message', '')
    show_keys_json = node_config.get('show_state_keys', '[]')
    timeout = node_config.get('timeout_seconds', 300)

    # Parse state keys to show
    try:
        show_keys = json.loads(show_keys_json)
    except json.JSONDecodeError:
        show_keys = []

    # Build context from state
    context = {}
    for key in show_keys:
        if key in state:
            context[key] = state[key]

    # Request approval (this pauses execution)
    approval_request = {
        'title': title,
        'message': message,
        'context': context,
        'timeout': timeout,
        'workflow_id': state.get('_workflow_id'),
        'node_id': state.get('_current_node_id')
    }

    try:
        # Wait for approval with timeout
        approved = await asyncio.wait_for(
            approval_callback(approval_request),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # Auto-reject on timeout
        approved = False

    # Store result to state
    state['approval_result'] = 'approved' if approved else 'rejected'
    state['approval_timestamp'] = datetime.now().isoformat()

    return {
        'success': True,
        'output': 'approved' if approved else 'rejected',
        'next': 'approved' if approved else 'rejected',
        'state_updates': {
            'approval_result': state['approval_result'],
            'approval_timestamp': state['approval_timestamp']
        }
    }
```

### Workflow Runner Integration

**File:** `backend/runner/workflow_runner.py`

Needs to support approval callback:

```python
class WorkflowRunner:
    def __init__(self, approval_handler=None):
        self.approval_handler = approval_handler or default_approval_handler

    async def execute_node(self, node, state):
        if node['type'] == 'human_approval':
            return await execute_human_approval_node(
                node['config'],
                state,
                self.approval_handler
            )
        # ... other node types
```

### Frontend Approval UI Component

**File:** `frontend/public/js/ui/approval-modal.js` (NEW)

```javascript
export function createApprovalModal(request) {
    const modal = document.createElement('div');
    modal.className = 'approval-modal-overlay';

    const dialog = document.createElement('div');
    dialog.className = 'approval-modal';

    // Title
    const title = document.createElement('h2');
    title.textContent = request.title;
    dialog.appendChild(title);

    // Message
    const message = document.createElement('p');
    message.textContent = request.message;
    dialog.appendChild(message);

    // Context
    if (request.context && Object.keys(request.context).length > 0) {
        const contextHeader = document.createElement('h3');
        contextHeader.textContent = 'Context:';
        dialog.appendChild(contextHeader);

        const contextList = document.createElement('ul');
        for (const [key, value] of Object.entries(request.context)) {
            const item = document.createElement('li');
            item.textContent = `${key}: ${JSON.stringify(value)}`;
            contextList.appendChild(item);
        }
        dialog.appendChild(contextList);
    }

    // Timeout countdown
    const countdown = document.createElement('div');
    countdown.className = 'approval-timeout';
    dialog.appendChild(countdown);

    // Buttons
    const actions = document.createElement('div');
    actions.className = 'approval-actions';

    const approveBtn = document.createElement('button');
    approveBtn.textContent = 'Approve';
    approveBtn.className = 'approval-btn approval-btn-approve';

    const rejectBtn = document.createElement('button');
    rejectBtn.textContent = 'Reject';
    rejectBtn.className = 'approval-btn approval-btn-reject';

    actions.append(approveBtn, rejectBtn);
    dialog.appendChild(actions);

    modal.appendChild(dialog);
    document.body.appendChild(modal);

    return new Promise((resolve) => {
        approveBtn.addEventListener('click', () => {
            modal.remove();
            resolve(true);
        });

        rejectBtn.addEventListener('click', () => {
            modal.remove();
            resolve(false);
        });

        // Auto-reject on timeout
        setTimeout(() => {
            if (document.body.contains(modal)) {
                modal.remove();
                resolve(false);
            }
        }, request.timeout * 1000);

        // Update countdown
        let remaining = request.timeout;
        const interval = setInterval(() => {
            remaining--;
            const mins = Math.floor(remaining / 60);
            const secs = remaining % 60;
            countdown.textContent = `Auto-rejects in: ${mins}:${secs.toString().padStart(2, '0')}`;
            if (remaining <= 0 || !document.body.contains(modal)) {
                clearInterval(interval);
            }
        }, 1000);
    });
}
```

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_human_approval_approved():
    config = {
        "title": "Test",
        "message": "Approve this?",
        "show_state_keys": '["action"]',
        "timeout_seconds": 10
    }
    state = {"action": "test_action"}

    # Mock approval callback that immediately approves
    async def mock_approval(request):
        return True

    result = await execute_human_approval_node(config, state, mock_approval)

    assert result['next'] == 'approved'
    assert state['approval_result'] == 'approved'

@pytest.mark.asyncio
async def test_human_approval_timeout():
    config = {
        "title": "Test",
        "message": "Approve this?",
        "timeout_seconds": 1
    }
    state = {}

    # Mock callback that never responds
    async def mock_approval(request):
        await asyncio.sleep(10)  # Longer than timeout
        return True

    result = await execute_human_approval_node(config, state, mock_approval)

    assert result['next'] == 'rejected'
    assert state['approval_result'] == 'rejected'
```

## Files Modified

- `frontend/public/js/nodes/schemas.js` - Already had human_approval schema
- `frontend/public/js/nodes/base.js` - Added interrupt property to BaseNode
- `frontend/public/js/graph/serializer.js` - Serialize interrupt config to backend
- `frontend/public/js/nodes/port.js` - Added approved/rejected output ports
- `frontend/public/js/nodes/index.js` - Auto-set interrupt on human_approval nodes
- `frontend/public/js/palette/categories.js` - Added human_approval to Control
- `frontend/public/js/api/run.js` - Added getCheckpoint() and hitlEdit() endpoints
- `frontend/public/js/ui/approval-modal.js` - NEW modal UI with countdown timer
- `frontend/public/js/ui/run-controls.js` - Detect paused status and drive approval flow
- `frontend/public/js/ui/status.js` - Added PAUSED status
- `frontend/public/css/layout.css` - Approval modal styles
- `frontend/tests/api/run.test.js` - Tests for new API endpoints
- `frontend/tests/ui/run-controls.test.js` - Tests for approval handling
- `frontend/tests/nodes/port.test.js` - Tests for new port types
- `backend/nodes/control/human_approval.py` - NEW node executor
- `backend/runner/node_factory.py` - Wired HumanApprovalNode into factory
- `backend/tests/test_nodes_human_approval.py` - Unit tests for approval logic
- `backend/tests/test_node_registry.py` - Updated expected types list

## Implementation Notes

**Date:** 2026-01-07

- Leverages existing backend HITL interrupt infrastructure (already implemented)
- Human approval nodes automatically set `interrupt.before = true`
- When run reaches approval node, backend pauses with `status: "paused"`, `pause_reason: "interrupt"`
- Frontend run controller detects pause, fetches checkpoint state, and shows modal
- Modal displays title, message, context from state, and countdown timer
- User clicks Approve or Reject (or timeout auto-rejects)
- Frontend calls `/hitl/edit` with `state_patch: { approval_result: "approved|rejected" }`
- Backend resumes execution; node reads decision from state and writes approval record
- Two output ports (approved/rejected) enable routing based on decision
- All backend tests pass (10/10)
- All frontend tests pass for approval flow (79/83 total, 4 pre-existing failures unrelated)
