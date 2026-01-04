import test from "node:test";
import assert from "node:assert/strict";

import { findContainingContainerId } from "../../public/js/nodes/container-math.js";

test("findContainingContainerId picks smallest containing container", () => {
  const nodeBoundsWorld = { x: 10, y: 10, width: 20, height: 20 };

  const containers = [
    { id: "big", boundsWorld: { x: 0, y: 0, width: 200, height: 200 } },
    { id: "small", boundsWorld: { x: 5, y: 5, width: 50, height: 50 } },
  ];

  const picked = findContainingContainerId({ nodeBoundsWorld, containers });
  assert.equal(picked, "small");
});

test("findContainingContainerId returns null when not contained", () => {
  const nodeBoundsWorld = { x: 10, y: 10, width: 20, height: 20 };

  const containers = [{ id: "c1", boundsWorld: { x: 100, y: 100, width: 50, height: 50 } }];

  const picked = findContainingContainerId({ nodeBoundsWorld, containers });
  assert.equal(picked, null);
});
