# BUGFIX: CSS Text Color and Form Input Fixes

**Status:** 🟢 Complete
**Type:** Bug Fix
**Completed:** 2026-01-07

## Issues Fixed

### 1. White Text on White Inputs

**Problem:**
Input fields and textareas in the properties panel had white text on white backgrounds, making them unreadable.

**Root Cause:**
The `.config-form-input`, `.config-form-select`, and `.config-form-textarea` classes were using:
- `background: var(--surface-0)` (white)
- `color: var(--chrome-fg)` (white - intended for dark backgrounds)

**Solution:**
Changed to explicit black text on white background:
```css
.config-form-input,
.config-form-select,
.config-form-textarea {
  background: #ffffff;
  color: #000000; /* Black text on white background */
}
```

Also updated `.properties-input` and `.properties-textarea`:
```css
.properties-input,
.properties-textarea {
  background: #ffffff;
  color: #000000; /* Always black text on white input */
}
```

### 2. [object Object] in Textareas

**Problem:**
Router node's `conditions` field (and other array/object fields) displayed as `[object Object]` in textareas instead of readable JSON.

**Root Cause:**
The `createTextarea()` function directly assigned object values to `textarea.value`, which JavaScript converts to `[object Object]`.

**Solution:**
Added JSON stringification for display and parsing for save:

**Display (createTextarea):**
```javascript
function createTextarea(field, value) {
  const textarea = el("textarea", "config-form-textarea");

  // Convert objects/arrays to JSON string for display
  let displayValue = value ?? field.default ?? "";
  if (typeof displayValue === "object" && displayValue !== null) {
    displayValue = JSON.stringify(displayValue, null, 2);
  }

  textarea.value = displayValue;
  // ... rest of function
}
```

**Save (collectFormConfig):**
```javascript
} else if (fieldType === "textarea") {
  // For textareas, try to parse as JSON (for arrays/objects)
  const val = input.value.trim();
  if (val) {
    try {
      // Try parsing as JSON first
      config[key] = JSON.parse(val);
    } catch (e) {
      // If not valid JSON, store as string
      config[key] = val;
    }
  }
}
```

### 3. Default Text Color

**Problem:**
No global default text color was set, relying on CSS variables that could be inappropriate for different contexts.

**Solution:**
Added explicit default in `.app-shell`:
```css
.app-shell {
  color: #000000; /* Default to black text everywhere */
}
```

## Files Modified

- `frontend/public/css/layout.css`
  - Added black default color to `.app-shell`
  - Fixed `.properties-input` and `.properties-textarea`
  - Fixed `.config-form-input`, `.config-form-select`, `.config-form-textarea`
  - Added select element black text rules

- `frontend/public/js/ui/node-properties.js`
  - Updated `createTextarea()` to stringify objects/arrays
  - Updated `collectFormConfig()` to parse JSON from textareas

## Testing

✅ Start node Target URL field - black text visible
✅ Router node Conditions field - shows formatted JSON array
✅ Edit JSON in textarea - properly parses back to array
✅ LLM node Prompt field - black text visible
✅ All select dropdowns - black text
✅ Number inputs - black text
✅ Checkbox labels - black text

## Design Principle Established

**Rule:** Default to black text everywhere, explicitly set white only for dark backgrounds.

**Implementation:**
- Body/containers: Black text by default
- Dark sidebars: `color: var(--chrome-fg)` (white) explicitly set
- All form inputs: `color: #000000` explicitly set
- Textareas: `color: #000000` explicitly set
- Select elements: `color: #000000` explicitly set

This prevents future occurrences of white-on-white text issues.

## Impact

- Improved readability of all form inputs
- Router node (and other nodes with complex config) now properly editable
- Consistent text color across entire application
- Better UX for node configuration
