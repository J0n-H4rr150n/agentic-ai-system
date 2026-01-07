# F00013_S005: Accurate Node Configuration Schemas

**Status:** 🟢 Complete
**Feature:** F00013 Canvas UI Enhancements
**Completed:** 2026-01-07

## Objective

Ensure all node configuration schemas match the actual configs used in workflows, providing accurate form fields for each node type.

## Acceptance Criteria

- [x] All node schemas match actual workflow configs
- [x] Start node shows `initial_state.target_url` field
- [x] Browser node has action, url_key, observation_mode, output_key
- [x] LLM node has model, prompt, json_mode, output_key
- [x] Router node has output_key, default_output, conditions array
- [x] End node has result_key field
- [x] All other node types have proper schemas

## Implementation

### Files Modified

- `frontend/public/js/nodes/schemas.js` - Complete rewrite

### Schema Examples

**Start Node:**
```javascript
start: {
  fields: [
    {
      key: 'initial_state.target_url',
      label: 'Target URL',
      type: 'url',
      placeholder: 'http://localhost:10303/',
      help: 'Initial URL to start the workflow'
    }
  ]
}
```

**Browser Node:**
```javascript
browser: {
  fields: [
    { key: 'action', type: 'select', options: ['navigate', 'click', 'type', 'screenshot'] },
    { key: 'url_key', type: 'text', default: 'target_url' },
    { key: 'observation_mode', type: 'select', options: ['visual', 'text', 'dom', 'hybrid'] },
    { key: 'output_key', type: 'text', default: 'browser_output' }
  ]
}
```

**LLM Node:**
```javascript
llm: {
  fields: [
    { key: 'model', type: 'select', options: ['gemini-1.5-flash', 'gemini-2.5-pro', ...] },
    { key: 'prompt', type: 'textarea', rows: 4, required: true },
    { key: 'json_mode', type: 'checkbox', default: false },
    { key: 'output_key', type: 'text', default: 'llm_output' }
  ]
}
```

**Router Node:**
```javascript
router: {
  fields: [
    { key: 'output_key', type: 'text' },
    { key: 'default_output', type: 'text', default: 'default' },
    { key: 'conditions', type: 'textarea', rows: 6, help: 'JSON array' }
  ]
}
```

### Nested Key Support

Added support for nested keys like `initial_state.target_url`:

```javascript
export function getDefaultConfig(type) {
  const schema = getSchemaForType(type);
  if (!schema) return {};

  const config = {};
  for (const field of schema.fields) {
    if (field.default !== undefined) {
      if (field.key.includes('.')) {
        // Handle nested: 'initial_state.target_url'
        const parts = field.key.split('.');
        let current = config;
        for (let i = 0; i < parts.length - 1; i++) {
          if (!current[parts[i]]) {
            current[parts[i]] = {};
          }
          current = current[parts[i]];
        }
        current[parts[parts.length - 1]] = field.default;
      } else {
        config[field.key] = field.default;
      }
    }
  }
  return config;
}
```

## Testing

✅ Start node shows Target URL field
✅ Browser node shows all 4 fields correctly
✅ LLM node shows model dropdown with correct options
✅ Router node shows conditions textarea
✅ End node shows result_key field
✅ Form changes auto-sync to JSON (already implemented)
✅ All field types render correctly (text, textarea, select, checkbox, number, url)
