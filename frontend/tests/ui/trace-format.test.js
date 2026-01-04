import test from "node:test";
import assert from "node:assert/strict";

import {
  buildStepDetailText,
  getScreenshotBase64FromOutput,
  sanitizeForDisplay,
} from "../../public/js/ui/trace/detail.js";

test("getScreenshotBase64FromOutput returns null for non-objects", () => {
  assert.equal(getScreenshotBase64FromOutput(null), null);
  assert.equal(getScreenshotBase64FromOutput("no"), null);
  assert.equal(getScreenshotBase64FromOutput(123), null);
});

test("getScreenshotBase64FromOutput detects common screenshot keys", () => {
  assert.equal(getScreenshotBase64FromOutput({ screenshot: "abc" }), "abc");
  assert.equal(getScreenshotBase64FromOutput({ screenshot_base64: "def" }), "def");
  assert.equal(getScreenshotBase64FromOutput({ screenshot_som: "ghi" }), "ghi");
});

test("sanitizeForDisplay omits large base64 strings", () => {
  const big = "a".repeat(200);
  const sanitized = sanitizeForDisplay({ screenshot: big, other: 1 });
  assert.deepEqual(sanitized, { screenshot: "<base64 omitted>", other: 1 });
});

test("buildStepDetailText formats input/output and includes error", () => {
  const step = {
    input: { foo: 1 },
    output: { bar: 2 },
    error: "boom",
  };

  const { inputText, outputText, errorText } = buildStepDetailText(step);

  assert.match(inputText, /"foo"/);
  assert.match(outputText, /"bar"/);
  assert.equal(errorText, "boom");
});
