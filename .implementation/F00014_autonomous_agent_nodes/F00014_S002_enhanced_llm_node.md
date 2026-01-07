# F00014_S002: Enhanced LLM Node with Structured Output

**Status:** � Complete
**Feature:** F00014 Autonomous Agent Nodes
**Started:** 2026-01-07
**Completed:** 2026-01-07

## Objective

Enhance the LLM node to support system prompts and structured JSON output schemas, enabling autonomous agents to produce consistent, parseable decision data including confidence scores, actions, findings, and reasoning.

## Acceptance Criteria

- [x] `system_prompt` field added to LLM schema
- [x] `output_schema` field for defining expected JSON structure
- [x] Backend enforces/validates output schema
- [x] Each schema field automatically stored to separate state keys
- [x] LLM can output: response, confidence, action, findings, reasoning, etc.

## Benefits

- **Better Instructions** - System prompts guide AI behavior
- **Structured Data** - No parsing magic, just JSON
- **Router-Friendly** - Easy to check confidence, action type, etc.
- **Observable** - Track AI reasoning and decisions
- **Composable** - Output feeds into conditional logic

## Implementation

### Frontend Schema Enhancement

**File:** `frontend/public/js/nodes/schemas.js`

Add to existing `llm` schema fields:

```javascript
{
    key: 'system_prompt',
    label: 'System Prompt',
    type: 'textarea',
    placeholder: 'You are an expert web security analyst...',
    rows: 3,
    help: 'System-level instructions for the LLM'
},
{
    key: 'output_schema',
    label: 'Output Schema (JSON)',
    type: 'textarea',
    placeholder: JSON.stringify({
        response: "string",
        confidence: "number",
        action: "string",
        findings: "array",
        reasoning: "string"
    }, null, 2),
    rows: 6,
    help: 'Expected output structure - enforces structured JSON'
}
```

### Example Usage

**Input:**
- System Prompt: "You are a web analyst. Always output confidence 0-1."
- Prompt: "Analyze {{target_url}} for login forms"
- Output Schema:
  ```json
  {
    "response": "string",
    "confidence": "number",
    "action": "string",
    "findings": "array"
  }
  ```

**LLM Output:**
```json
{
  "response": "Found 2 login forms on the page",
  "confidence": 0.92,
  "action": "extract_forms",
  "findings": ["#login-form-1", "#login-form-2"]
}
```

**State After Execution:**
```javascript
state.llm_response = "Found 2 login forms on the page"
state.llm_confidence = 0.92
state.llm_action = "extract_forms"
state.llm_findings = ["#login-form-1", "#login-form-2"]
```

### Backend Implementation

**File:** `backend/runner/nodes/llm.py`

```python
import json
from typing import Dict, Any

async def execute_llm_node(node_config: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute LLM node with optional system prompt and structured output.
    """
    model = node_config.get('model')
    prompt = node_config.get('prompt', '')
    system_prompt = node_config.get('system_prompt', '')
    output_schema = node_config.get('output_schema')
    json_mode = node_config.get('json_mode', False)

    # Parse output schema if provided
    expected_schema = None
    if output_schema:
        try:
            expected_schema = json.loads(output_schema)
            json_mode = True  # Force JSON mode if schema provided
        except json.JSONDecodeError:
            # Invalid schema - log warning but continue
            pass

    # Build messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Template substitution in prompt
    rendered_prompt = render_template(prompt, state)
    messages.append({"role": "user", "content": rendered_prompt})

    # Call LLM
    response = await call_llm(
        model=model,
        messages=messages,
        json_mode=json_mode,
        response_schema=expected_schema
    )

    # Parse and store response
    state_updates = {}

    if expected_schema and json_mode:
        # Structured output - parse JSON and store fields separately
        try:
            parsed = json.loads(response)
            for key, value in parsed.items():
                state_key = f"llm_{key}"
                state[state_key] = value
                state_updates[state_key] = value
        except json.JSONDecodeError:
            # Fallback to plain output
            output_key = node_config.get('output_key', 'llm_output')
            state[output_key] = response
            state_updates[output_key] = response
    else:
        # Plain text output
        output_key = node_config.get('output_key', 'llm_output')
        state[output_key] = response
        state_updates[output_key] = response

    return {
        'success': True,
        'output': response,
        'next': 'default',
        'state_updates': state_updates
    }


def render_template(template: str, state: Dict[str, Any]) -> str:
    """
    Replace {{key}} placeholders with state values.
    """
    import re

    def replace_var(match):
        key = match.group(1)
        return str(state.get(key, f"{{{{key}}}}"))

    return re.sub(r'\{\{(\w+)\}\}', replace_var, template)
```

## Router Integration Example

With structured LLM output, Router can easily check confidence:

```javascript
// Router conditions
[
  {
    "var": "llm_confidence",
    "op": "less_than",
    "value": 0.5,
    "output": "low_confidence"  // → Go to human approval
  },
  {
    "var": "llm_confidence",
    "op": "greater_equal",
    "value": 0.5,
    "output": "high_confidence"  // → Execute action
  }
]
```

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_llm_structured_output():
    config = {
        "model":  "gemini-1.5-flash",
        "system_prompt": "You are a helper",
        "prompt": "Analyze {{url}}",
        "output_schema": '{"response": "string", "confidence": "number"}'
    }
    state = {"url": "http://test.com"}

    # Mock LLM to return structured JSON
    with patch('llm.call_llm', return_value='{"response": "test", "confidence": 0.8}'):
        result = await execute_llm_node(config, state)

    assert state['llm_response'] == "test"
    assert state['llm_confidence'] == 0.8
    assert result['success'] == True
```

## Files Modified

- `frontend/public/js/nodes/schemas.js` - Already had system_prompt and output_schema fields
- `backend/nodes/llm/base.py` - Enhanced LLMCallNode with template/schema support
- `backend/nodes/llm/prompt_template.py` - New helper for {{path}} template rendering
- `backend/nodes/llm/output_schema.py` - New helper for schema parsing and validation
- `backend/tests/test_nodes_llm_base.py` - Updated with new behavior tests
- `backend/tests/test_llm_prompt_template.py` - Unit tests for template rendering
- `backend/tests/test_llm_output_schema.py` - Unit tests for schema validation

## Implementation Notes

**Date:** 2026-01-07

- Prompt templates support `{{path}}` and `{{nested.path}}` syntax from state
- System prompts are prefixed as `System:\n...\n\nUser:\n...` before user prompt
- Output schema forces `json_mode=True` on LLM calls
- Schema validation extracts fields and writes them as `llm_{field}` in state
- Missing required fields raise validation errors
- All backend tests pass (10/10)
- Frontend tests pass (79/83, 4 pre-existing failures unrelated to this work)
