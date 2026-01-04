import test from "node:test";
import assert from "node:assert/strict";

import { rectContainsPoint } from "../../public/js/utils/geometry.js";

test("rectContainsPoint works for inside/outside", () => {
  const rect = { x: 10, y: 20, width: 30, height: 40 };

  assert.equal(rectContainsPoint(rect, { x: 10, y: 20 }), true);
  assert.equal(rectContainsPoint(rect, { x: 40, y: 60 }), true);
  assert.equal(rectContainsPoint(rect, { x: 41, y: 60 }), false);
  assert.equal(rectContainsPoint(rect, { x: 40, y: 61 }), false);
});

test("rectContainsPoint throws on invalid args", () => {
  assert.throws(() => rectContainsPoint(null, { x: 0, y: 0 }));
  assert.throws(() => rectContainsPoint({ x: 0, y: 0, width: 1, height: 1 }, null));
});
