import test from "node:test";
import assert from "node:assert/strict";

import {
  clampScale,
  createViewport,
  panByScreenDelta,
  screenToWorld,
  worldToScreen,
  zoomAtScreenPoint,
} from "../../public/js/canvas/viewport.js";

test("clampScale clamps to 0.25..4", () => {
  assert.equal(clampScale(0.1), 0.25);
  assert.equal(clampScale(10), 4);
  assert.equal(clampScale(1), 1);
});

test("panByScreenDelta changes offsets in world units", () => {
  const viewport = createViewport();
  viewport.scale = 2;

  panByScreenDelta(viewport, { dx: 20, dy: -10 });
  assert.equal(viewport.offsetX, 10);
  assert.equal(viewport.offsetY, -5);
});

test("zoomAtScreenPoint preserves world point under cursor", () => {
  const viewport = createViewport();
  viewport.offsetX = 5;
  viewport.offsetY = -3;
  viewport.scale = 1;

  const cursor = { x: 100, y: 50 };
  const worldBefore = screenToWorld(cursor, viewport);

  zoomAtScreenPoint(viewport, cursor, 2);

  const worldAfter = screenToWorld(cursor, viewport);
  assert.ok(Math.abs(worldAfter.x - worldBefore.x) < 1e-9);
  assert.ok(Math.abs(worldAfter.y - worldBefore.y) < 1e-9);

  const roundTrip = worldToScreen(worldBefore, viewport);
  assert.ok(Math.abs(roundTrip.x - cursor.x) < 1e-9);
  assert.ok(Math.abs(roundTrip.y - cursor.y) < 1e-9);
});
