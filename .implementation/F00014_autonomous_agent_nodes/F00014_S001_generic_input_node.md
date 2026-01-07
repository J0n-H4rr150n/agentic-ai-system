# F00014_S001: Generic Input Node

**Status:** � Complete
**Feature:** F00014 Autonomous Agent Nodes
**Started:** 2026-01-07
**Completed:** 2026-01-07

## Objective

Create a generic `input` node type that allows users to define any string/text input for their workflow, replacing the need for hardcoded Start node fields.

## Acceptance Criteria

- [x] `input` node type added to `schemas.js`
- [x] Configurable label field
- [x] Configurable value field (textarea)
- [x] Configurable output_key field
- [x] Node appears in palette
- [x] Backend executor stores value to state
- [x] Multiple input nodes can exist in one workflow

## Use Cases

1. **Target URL Input** - Specify web page to analyze
2. **User Prompt Input** - Natural language instructions
3. **System Instructions** - AI behavior guidelines
4. **API Keys** - Configuration values
5. **Test Data** - Sample inputs for testing

## Implementation

### Frontend Schema

**File:** `frontend/public/js/nodes/schemas.js`

```javascript
input: {
    fields: [
        {
            key: 'label',
            label: 'Input Label',
            type: 'text',
            placeholder: 'e.g., "Target URL"',
            required: true,
            help: 'Descriptive name for this input'
        },
        {
            key: 'value',
            label: 'Value',
            type: 'textarea',
            placeholder: 'Enter the input value...',
            rows: 3,
            required: true,
            help: 'The actual input data'
        },
        {
            key: 'output_key',
            label: 'Output Key',
            type: 'text',
            placeholder: 'target_url',
            default: 'input_value',
            required: true,
            help: 'State key to store this value'
        }
    ]
}
```

### Node Visual

**File:** `frontend/public/js/nodes/input.js` (NEW)

```javascript
export class InputNode extends BaseNode {
    constructor(data) {
        super(data);
        this.type = 'input';
        this.width = 180;
        this.height = 80;
    }

    render(ctx, options = {}) {
        const { x, y, width, height } = this;
        const scale = options.scale || 1;

        // Background
        ctx.fillStyle = '#f0f9ff'; // Light blue
        ctx.fillRect(x, y, width, height);

        // Border
        ctx.strokeStyle = options.selected ? '#0f172a' : '#3b82f6';
        ctx.lineWidth = options.selected ? 2 : 1;
        ctx.strokeRect(x, y, width, height);

        // Icon
        ctx.font = `${16 * scale}px sans-serif`;
        ctx.fillStyle = '#3b82f6';
        ctx.fillText('📝', x + 10, y + 30);

        // Label
        const label = this.config.label || 'Input';
        ctx.font = `${12 * scale}px sans-serif`;
        ctx.fillStyle = '#1e293b';
        ctx.fillText(label, x + 40, y + 30);

        // Output key hint
        const outputKey = this.config.output_key || 'input_value';
        ctx.font = `${10 * scale}px sans-serif`;
        ctx.fillStyle = '#64748b';
        ctx.fillText(`→ ${outputKey}`, x + 10, y + height - 10);

        // Output port (right side)
        this.renderPort(ctx, {
            x: x + width,
            y: y + height / 2,
            type: 'output',
            scale
        });
    }
}
```

### Backend Executor

**File:** `backend/runner/nodes/input.py` (NEW)

```python
"""
Input node executor.
Stores configured value to workflow state.
"""

async def execute_input_node(node_config: dict, state: dict) -> dict:
    """
    Execute input node.

    Args:
        node_config: Node configuration containing value and output_key
        state: Current workflow state

    Returns:
        Execution result with success status
    """
    output_key = node_config.get('output_key', 'input_value')
    value = node_config.get('value', '')

    # Store to state
    state[output_key] = value

    return {
        'success': True,
        'output': value,
        'next': 'default',
        'state_updates': {
            output_key: value
        }
    }
```

### Template

**File:** `backend/api/routes/templates.py`

Add to templates list:
```python
{
    "id": "input",
    "name": "Input",
    "type": "input",
    "category": "COMMON",
    "icon": "📝",
    "description": "Generic input value",
    "defaultConfig": {
        "label": "Input",
        "value": "",
        "output_key": "input_value"
    }
}
```

## Testing

### Unit Tests

**File:** `backend/tests/runner/nodes/test_input.py`

```python
import pytest
from backend.runner.nodes.input import execute_input_node

@pytest.mark.asyncio
async def test_input_node_stores_to_state():
    config = {
        "value": "http://example.com",
        "output_key": "target_url"
    }
    state = {}

    result = await execute_input_node(config, state)

    assert result['success'] == True
    assert state['target_url'] == "http://example.com"

@pytest.mark.asyncio
async def test_input_node_default_key():
    config = {
        "value": "test value"
    }
    state = {}

    result = await execute_input_node(config, state)

    assert state['input_value'] == "test value"
```

### Manual Testing

1. Add Input node to canvas
2. Configure label: "Target URL"
3. Configure value: "http://localhost:10303/"
4. Configure output_key: "target_url"
5. Connect to LLM node
6. Run workflow
7. Verify state contains `target_url` key

## Files Modified

- `frontend/public/js/nodes/schemas.js` - Already had input schema defined
- `frontend/public/js/palette/categories.js` - Added input to Control category
- `frontend/public/js/nodes/port.js` - Added output-only ports for input type
- `backend/nodes/control/input.py` - New node executor
- `backend/runner/node_factory.py` - Wired InputNode into factory
- `backend/tests/test_nodes_input.py` - Unit tests for input node
- `backend/tests/test_node_registry.py` - Updated expected types list

## Implementation Notes

**Date:** 2026-01-07

- Backend node executor reads `config.value` and writes to state under `config.output_key` (default: `input_value`)
- Frontend palette now includes input in Control category
- Ports are output-only (input nodes have no upstream dependencies)
- All backend tests pass (10/10)
- Frontend tests pass (79/83, 4 pre-existing failures unrelated to this work)
