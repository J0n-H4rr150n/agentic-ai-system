import test from "node:test";
import assert from "node:assert/strict";

import {
  clampSizeWorld,
  computeResizeDeltaWorld,
  computeResizedSizeWorld,
  snapSizeToGrid,
} from "../../public/js/selection/resize-math.js";

test("computeResizeDeltaWorld computes dx/dy", () => {
  assert.deepEqual(
    computeResizeDeltaWorld({ x: 15, y: 25 }, { x: 10, y: 20 }),
    { dx: 5, dy: 5 },
  );
});

test("computeResizedSizeWorld applies delta", () => {
  assert.deepEqual(
    computeResizedSizeWorld({ width: 100, height: 80 }, { dx: 20, dy: -10 }),
    { width: 120, height: 70 },
  );
});

test("clampSizeWorld enforces minimums", () => {
  assert.deepEqual(
    clampSizeWorld({ width: 10, height: 10 }, { minWidth: 50, minHeight: 40 }),
    { width: 50, height: 40 },
  );
});

test("snapSizeToGrid snaps both axes", () => {
  assert.deepEqual(snapSizeToGrid({ width: 14, height: 15 }, 10), { width: 10, height: 20 });
});
