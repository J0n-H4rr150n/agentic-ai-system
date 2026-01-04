import test from "node:test";
import assert from "node:assert/strict";

import { NodeManager } from "../../public/js/nodes/index.js";
import { BaseNode } from "../../public/js/nodes/base.js";

test("getNodeAtWorldPoint returns topmost node", () => {
  const manager = new NodeManager();
  const bottom = new BaseNode({
    id: "bottom",
    type: "t",
    position: { x: 0, y: 0 },
    size: { width: 100, height: 100 },
  });
  const top = new BaseNode({
    id: "top",
    type: "t",
    position: { x: 0, y: 0 },
    size: { width: 100, height: 100 },
  });

  manager.add(bottom);
  manager.add(top);

  const hit = manager.getNodeAtWorldPoint({ x: 10, y: 10 });
  assert.equal(hit.id, "top");
});

test("bringToFront changes z-order", () => {
  const manager = new NodeManager();
  const a = new BaseNode({ id: "a", type: "t" });
  const b = new BaseNode({ id: "b", type: "t" });

  manager.add(a);
  manager.add(b);

  manager.bringToFront(a);
  assert.equal(manager.getNodes()[manager.getNodes().length - 1].id, "a");
});
