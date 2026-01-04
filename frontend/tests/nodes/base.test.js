import test from "node:test";
import assert from "node:assert/strict";

import { BaseNode } from "../../public/js/nodes/base.js";

test("BaseNode containsWorldPoint uses node bounds", () => {
  const node = new BaseNode({
    id: "n1",
    type: "test",
    position: { x: 100, y: 200 },
    size: { width: 50, height: 60 },
  });

  assert.equal(node.containsWorldPoint({ x: 100, y: 200 }), true);
  assert.equal(node.containsWorldPoint({ x: 150, y: 260 }), true);
  assert.equal(node.containsWorldPoint({ x: 151, y: 260 }), false);
  assert.equal(node.containsWorldPoint({ x: 150, y: 261 }), false);
});
