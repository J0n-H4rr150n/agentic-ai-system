import test from "node:test";
import assert from "node:assert/strict";

import { createViewport, screenToWorld } from "../../public/js/canvas/viewport.js";
import { computeDropTopLeftWorld, snapToGrid } from "../../public/js/palette/drop-math.js";

test("snapToGrid rounds to nearest grid line", () => {
  assert.equal(snapToGrid(0, 10), 0);
  assert.equal(snapToGrid(4, 10), 0);
  assert.equal(snapToGrid(5, 10), 10);
  assert.equal(snapToGrid(15, 10), 20);
});

test("computeDropTopLeftWorld centers then snaps", () => {
  const viewport = createViewport();
  viewport.scale = 2;
  viewport.offsetX = 10;
  viewport.offsetY = -5;

  const screenPoint = { x: 100, y: 50 };
  const worldAtCursor = screenToWorld(screenPoint, viewport);

  const nodeSize = { width: 180, height: 72 };
  const topLeft = computeDropTopLeftWorld({
    screenPoint,
    viewport,
    nodeSize,
    gridSize: 10,
  });

  // Prior to snapping, top-left is centered at cursor in world.
  const rawX = worldAtCursor.x - nodeSize.width / 2;
  const rawY = worldAtCursor.y - nodeSize.height / 2;

  assert.equal(Math.abs(topLeft.x % 10), 0);
  assert.equal(Math.abs(topLeft.y % 10), 0);
  assert.ok(Math.abs(topLeft.x - rawX) <= 5);
  assert.ok(Math.abs(topLeft.y - rawY) <= 5);
});
