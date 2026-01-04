import test from "node:test";
import assert from "node:assert/strict";

import {
  computeDragOffsetWorld,
  computeDraggedTopLeftWorld,
  snapPositionToGrid,
} from "../../public/js/selection/move-math.js";

test("computeDragOffsetWorld and computeDraggedTopLeftWorld are inverse", () => {
  const cursor = { x: 12.5, y: -7 };
  const nodePos = { x: 2.5, y: -10 };

  const offset = computeDragOffsetWorld(cursor, nodePos);
  const moved = computeDraggedTopLeftWorld(cursor, offset);

  assert.deepEqual(moved, nodePos);
});

test("snapPositionToGrid snaps both axes", () => {
  const snapped = snapPositionToGrid({ x: 14, y: 15 }, 10);
  assert.deepEqual(snapped, { x: 10, y: 20 });
});
