import test from "node:test";
import assert from "node:assert/strict";

import { computeCubicBezierControlPoints } from "../../public/js/wires/bezier.js";

test("computeCubicBezierControlPoints produces finite control points", () => {
  const { c1World, c2World } = computeCubicBezierControlPoints({
    startWorld: { x: 0, y: 0 },
    endWorld: { x: 100, y: 50 },
  });

  for (const p of [c1World, c2World]) {
    assert.equal(Number.isFinite(p.x), true);
    assert.equal(Number.isFinite(p.y), true);
  }
});

test("computeCubicBezierControlPoints offsets in X direction", () => {
  const { c1World, c2World } = computeCubicBezierControlPoints({
    startWorld: { x: 10, y: 5 },
    endWorld: { x: 110, y: 25 },
  });

  assert.ok(c1World.x > 10);
  assert.ok(c2World.x < 110);
  assert.equal(c1World.y, 5);
  assert.equal(c2World.y, 25);
});
