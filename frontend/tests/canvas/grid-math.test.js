import test from "node:test";
import assert from "node:assert/strict";

import { getGridLinePositions } from "../../public/js/canvas/grid-math.js";

test("getGridLinePositions returns multiples within bounds", () => {
  const bounds = { left: 0, top: 0, right: 25, bottom: 25 };
  const { vertical, horizontal } = getGridLinePositions(bounds, 10);

  assert.deepEqual(vertical, [0, 10, 20, 30]);
  assert.deepEqual(horizontal, [0, 10, 20, 30]);
});

test("getGridLinePositions throws on invalid input", () => {
  assert.throws(() => getGridLinePositions(null, 10));
  assert.throws(() => getGridLinePositions({ left: 0, top: 0, right: 1 }, 10));
  assert.throws(() => getGridLinePositions({ left: 0, top: 0, right: 1, bottom: 1 }, 0));
});
