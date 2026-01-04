function safeJsonStringify(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return "<unserializable>";
  }
}

export function getScreenshotBase64FromOutput(output) {
  if (!output || typeof output !== "object") {
    return null;
  }

  const keys = ["screenshot", "screenshot_base64", "screenshot_som"];

  for (const key of keys) {
    const screenshot = output[key];
    if (typeof screenshot === "string" && screenshot.length > 0) {
      return screenshot;
    }
  }

  // Common case: node output is nested under an output_key (e.g. {browser_output: {...}})
  for (const value of Object.values(output)) {
    if (!value || typeof value !== "object") {
      continue;
    }
    for (const key of keys) {
      const screenshot = value[key];
      if (typeof screenshot === "string" && screenshot.length > 0) {
        return screenshot;
      }
    }
  }

  return null;
}

export function sanitizeForDisplay(value) {
  if (!value || typeof value !== "object") {
    return value;
  }

  const out = Array.isArray(value) ? value.slice() : { ...value };

  if (!Array.isArray(out) && typeof out === "object") {
    // Avoid huge base64 blobs in the JSON view.
    for (const key of ["screenshot", "screenshot_base64", "screenshot_som"]) {
      if (typeof out[key] === "string" && out[key].length > 100) {
        out[key] = "<base64 omitted>";
      }
    }
  }

  return out;
}

export function buildStepDetailText(step) {
  const input = sanitizeForDisplay(step?.input);
  const output = sanitizeForDisplay(step?.output);

  return {
    inputText: safeJsonStringify(input),
    outputText: safeJsonStringify(output),
    errorText: step?.error ? String(step.error) : null,
  };
}
