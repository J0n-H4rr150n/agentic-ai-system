import test from "node:test";
import assert from "node:assert/strict";

import { serializeGraph } from "../../public/js/graph/serializer.js";
import { NodeManager } from "../../public/js/nodes/index.js";
import { WireManager } from "../../public/js/wires/index.js";

test("serializeGraph includes nodes, edges, positions, configs", () => {
  const nodeManager = new NodeManager();
  const wireManager = new WireManager();

  const a = nodeManager.addFromPalette({ type: "start", title: "Start", position: { x: 10, y: 20 } });
  const b = nodeManager.addFromPalette({ type: "end", title: "End", position: { x: 110, y: 220 } });

  // Ensure configs are serialized as objects.
  a.config = { foo: "bar" };

  wireManager.createWire({
    from: { nodeId: a.id, portId: a.ports[0].id },
    to: { nodeId: b.id, portId: b.ports[0].id },
  });

  const graph = serializeGraph({ nodeManager, wireManager });

  assert.equal(graph.version, 1);
  assert.equal(Array.isArray(graph.nodes), true);
  assert.equal(Array.isArray(graph.edges), true);

  const nodeA = graph.nodes.find((n) => n.id === a.id);
  const nodeB = graph.nodes.find((n) => n.id === b.id);

  assert.ok(nodeA);
  assert.ok(nodeB);
  assert.deepEqual(nodeA.position, { x: 10, y: 20 });
  assert.deepEqual(nodeA.config, { foo: "bar" });
  assert.deepEqual(nodeB.position, { x: 110, y: 220 });
  assert.deepEqual(nodeB.config, {});

  assert.equal(graph.edges.length, 1);
  assert.equal(graph.edges[0].from.nodeId, a.id);
  assert.equal(graph.edges[0].to.nodeId, b.id);
});

test("serializeGraph excludes UI-only container nodes", () => {
  const nodeManager = new NodeManager();
  const wireManager = new WireManager();

  const container = nodeManager.addFromPalette({ type: "container", title: "Group", position: { x: 0, y: 0 } });
  const a = nodeManager.addFromPalette({ type: "start", title: "Start", position: { x: 10, y: 20 } });

  // Sanity check: container exists in node manager.
  assert.ok(container);
  assert.equal(container.type, "container");

  const graph = serializeGraph({ nodeManager, wireManager });
  assert.equal(graph.nodes.some((n) => n.type === "container"), false);
  assert.ok(graph.nodes.find((n) => n.id === a.id));
});
