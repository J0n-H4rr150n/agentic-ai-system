import test from "node:test";
import assert from "node:assert/strict";

import { isTraceCollapsed, setTraceCollapsed, TRACE_COLLAPSED_CLASS } from "../../public/js/ui/trace/collapse.js";

function createFakeElement() {
  const classes = new Set();
  return {
    classList: {
      add: (c) => classes.add(c),
      remove: (c) => classes.delete(c),
      contains: (c) => classes.has(c),
    },
    _classes: classes,
  };
}

test("setTraceCollapsed adds/removes workspace class", () => {
  const el = createFakeElement();

  assert.equal(isTraceCollapsed(el), false);

  setTraceCollapsed(el, true);
  assert.equal(isTraceCollapsed(el), true);
  assert.equal(el._classes.has(TRACE_COLLAPSED_CLASS), true);

  setTraceCollapsed(el, false);
  assert.equal(isTraceCollapsed(el), false);
});
