import test from "node:test";
import assert from "node:assert/strict";

import {
  Port,
  PORT_KIND,
  PORT_RADIUS_WORLD,
  computePortCentersWorld,
  createDefaultPortsForNodeType,
  getPortHitAtWorldPoint,
} from "../../public/js/nodes/port.js";

test("createDefaultPortsForNodeType uses start/end conventions", () => {
  const startPorts = createDefaultPortsForNodeType({ nodeId: "n1", type: "start" });
  assert.equal(startPorts.length, 1);
  assert.equal(startPorts[0].kind, PORT_KIND.OUTPUT);

  const endPorts = createDefaultPortsForNodeType({ nodeId: "n2", type: "end" });
  assert.equal(endPorts.length, 1);
  assert.equal(endPorts[0].kind, PORT_KIND.INPUT);

  const midPorts = createDefaultPortsForNodeType({ nodeId: "n3", type: "llm" });
  assert.equal(midPorts.length, 2);
  assert.equal(midPorts[0].kind, PORT_KIND.INPUT);
  assert.equal(midPorts[1].kind, PORT_KIND.OUTPUT);
});

test("computePortCentersWorld returns left for input and right for output", () => {
  const ports = [
    new Port({ id: "in", kind: PORT_KIND.INPUT }),
    new Port({ id: "out", kind: PORT_KIND.OUTPUT }),
  ];

  const bounds = { x: 10, y: 20, width: 100, height: 80 };
  const centers = computePortCentersWorld({ nodeBoundsWorld: bounds, ports });

  const input = centers.find((c) => c.kind === PORT_KIND.INPUT);
  const output = centers.find((c) => c.kind === PORT_KIND.OUTPUT);

  assert.ok(input);
  assert.ok(output);

  assert.equal(input.side, "left");
  assert.equal(output.side, "right");

  assert.equal(input.centerWorld.x, bounds.x - PORT_RADIUS_WORLD);
  assert.equal(output.centerWorld.x, bounds.x + bounds.width + PORT_RADIUS_WORLD);
});

test("getPortHitAtWorldPoint hits when cursor is within radius", () => {
  const ports = [new Port({ id: "in", kind: PORT_KIND.INPUT })];
  const bounds = { x: 0, y: 0, width: 100, height: 80 };

  const [info] = computePortCentersWorld({ nodeBoundsWorld: bounds, ports });
  const hit = getPortHitAtWorldPoint({
    nodeBoundsWorld: bounds,
    ports,
    worldPoint: { x: info.centerWorld.x, y: info.centerWorld.y },
  });

  assert.ok(hit);
  assert.equal(hit.port.id, "in");
});

test("getPortHitAtWorldPoint returns null when far away", () => {
  const ports = [new Port({ id: "in", kind: PORT_KIND.INPUT })];
  const bounds = { x: 0, y: 0, width: 100, height: 80 };

  const hit = getPortHitAtWorldPoint({
    nodeBoundsWorld: bounds,
    ports,
    worldPoint: { x: 9999, y: 9999 },
  });

  assert.equal(hit, null);
});
