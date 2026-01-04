function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export const PORT_KIND = Object.freeze({
  INPUT: "input",
  OUTPUT: "output",
});

export const PORT_RADIUS_WORLD = 6;

export class Port {
  constructor({ id, kind, label }) {
    if (!isNonEmptyString(id)) {
      throw new Error("Port id must be a non-empty string");
    }
    if (kind !== PORT_KIND.INPUT && kind !== PORT_KIND.OUTPUT) {
      throw new Error('Port kind must be "input" or "output"');
    }

    this.id = id;
    this.kind = kind;
    this.label = label ?? null;
  }
}

export function createDefaultPortsForNodeType({ nodeId, type }) {
  if (!isNonEmptyString(nodeId)) {
    throw new Error("nodeId must be a non-empty string");
  }
  if (!isNonEmptyString(type)) {
    throw new Error("type must be a non-empty string");
  }

  if (type === "start") {
    return [new Port({ id: `${nodeId}:out:1`, kind: PORT_KIND.OUTPUT })];
  }
  if (type === "end") {
    return [new Port({ id: `${nodeId}:in:1`, kind: PORT_KIND.INPUT })];
  }

  return [
    new Port({ id: `${nodeId}:in:1`, kind: PORT_KIND.INPUT }),
    new Port({ id: `${nodeId}:out:1`, kind: PORT_KIND.OUTPUT }),
  ];
}

function getPortSide(kind) {
  return kind === PORT_KIND.INPUT ? "left" : "right";
}

function distanceSquared(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return dx * dx + dy * dy;
}

export function computePortCentersWorld({ nodeBoundsWorld, ports }) {
  if (
    !nodeBoundsWorld ||
    !isFiniteNumber(nodeBoundsWorld.x) ||
    !isFiniteNumber(nodeBoundsWorld.y) ||
    !isFiniteNumber(nodeBoundsWorld.width) ||
    !isFiniteNumber(nodeBoundsWorld.height)
  ) {
    throw new Error("nodeBoundsWorld must be {x,y,width,height} with finite numbers");
  }
  if (!Array.isArray(ports)) {
    throw new Error("ports must be an array");
  }

  const inputs = ports.filter((p) => p.kind === PORT_KIND.INPUT);
  const outputs = ports.filter((p) => p.kind === PORT_KIND.OUTPUT);

  const inputCenters = computeSideCenters({
    nodeBoundsWorld,
    ports: inputs,
    side: "left",
  });
  const outputCenters = computeSideCenters({
    nodeBoundsWorld,
    ports: outputs,
    side: "right",
  });

  return [...inputCenters, ...outputCenters];
}

function computeSideCenters({ nodeBoundsWorld, ports, side }) {
  if (ports.length === 0) {
    return [];
  }

  const margin = 18;
  const available = Math.max(0, nodeBoundsWorld.height - margin * 2);
  const step = ports.length > 0 ? available / (ports.length + 1) : 0;

  const x =
    side === "left"
      ? nodeBoundsWorld.x - PORT_RADIUS_WORLD
      : nodeBoundsWorld.x + nodeBoundsWorld.width + PORT_RADIUS_WORLD;

  return ports.map((port, index) => {
    const y =
      available === 0
        ? nodeBoundsWorld.y + nodeBoundsWorld.height / 2
        : nodeBoundsWorld.y + margin + step * (index + 1);

    return {
      port,
      kind: port.kind,
      side,
      centerWorld: { x, y },
    };
  });
}

export function getPortHitAtWorldPoint({ nodeBoundsWorld, ports, worldPoint, hitRadiusWorld }) {
  if (!Array.isArray(ports)) {
    throw new Error("ports must be an array");
  }
  if (!worldPoint || !isFiniteNumber(worldPoint.x) || !isFiniteNumber(worldPoint.y)) {
    throw new Error("worldPoint must be {x,y} with finite numbers");
  }

  const radius = hitRadiusWorld ?? PORT_RADIUS_WORLD + 2;
  if (!isFiniteNumber(radius) || radius <= 0) {
    throw new Error("hitRadiusWorld must be a positive finite number");
  }

  const centers = computePortCentersWorld({ nodeBoundsWorld, ports });
  const r2 = radius * radius;

  for (const info of centers) {
    if (distanceSquared(worldPoint, info.centerWorld) <= r2) {
      return info;
    }
  }

  return null;
}

export function getPortSideForPort(port) {
  if (!(port instanceof Port)) {
    throw new Error("port must be a Port");
  }
  return getPortSide(port.kind);
}
