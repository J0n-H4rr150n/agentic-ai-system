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

test("updateParentForNode assigns parentId when contained", () => {
  const manager = new NodeManager();
  const container = manager.addFromPalette({ type: "container", title: "Container", position: { x: 0, y: 0 } });
  container.size = { width: 200, height: 200 };

  const node = new BaseNode({
    id: "child",
    type: "t",
    position: { x: 10, y: 10 },
    size: { width: 20, height: 20 },
  });
  manager.add(node);

  manager.updateParentForNode(node);
  assert.equal(node.parentId, container.id);
});

test("updateParentForNode clears parentId when not contained", () => {
  const manager = new NodeManager();
  manager.addFromPalette({ type: "container", title: "Container", position: { x: 0, y: 0 } });

  const node = new BaseNode({
    id: "child",
    type: "t",
    position: { x: 500, y: 500 },
    size: { width: 20, height: 20 },
  });
  node.parentId = "some-container";
  manager.add(node);

  manager.updateParentForNode(node);
  assert.equal(node.parentId, null);
});
