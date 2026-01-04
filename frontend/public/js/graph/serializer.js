function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function normalizeConfig(config) {
  if (config && typeof config === "object" && !Array.isArray(config)) {
    return config;
  }
  return {};
}

export function serializeGraph({ nodeManager, wireManager }) {
  if (!nodeManager || typeof nodeManager.getNodes !== "function") {
    throw new Error("nodeManager must provide getNodes()");
  }
  if (!wireManager || typeof wireManager.getWires !== "function") {
    throw new Error("wireManager must provide getWires()");
  }

  const nodes = nodeManager
    .getNodes()
    .filter((node) => node?.type !== "container")
    .map((node) => {
    if (!isNonEmptyString(node.id) || !isNonEmptyString(node.type)) {
      throw new Error("All nodes must have non-empty id and type");
    }

    return {
      id: node.id,
      type: node.type,
      title: node.title ?? node.type,
      position: { x: node.position?.x ?? 0, y: node.position?.y ?? 0 },
      size: {
        width: node.size?.width ?? 180,
        height: node.size?.height ?? 72,
      },
      ports: (node.ports ?? []).map((p) => ({
        id: p.id,
        kind: p.kind,
        label: p.label ?? null,
      })),
      config: normalizeConfig(node.config),
    };
    });

  const edges = wireManager.getWires().map((wire) => {
    if (!isNonEmptyString(wire.id)) {
      throw new Error("All wires must have non-empty id");
    }
    return {
      id: wire.id,
      from: { nodeId: wire.from.nodeId, portId: wire.from.portId },
      to: { nodeId: wire.to.nodeId, portId: wire.to.portId },
    };
  });

  return {
    version: 1,
    nodes,
    edges,
  };
}

export function stringifyGraph(graph) {
  return JSON.stringify(graph, null, 2);
}
