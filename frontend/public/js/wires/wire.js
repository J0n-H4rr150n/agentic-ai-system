function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

export class Wire {
  constructor({ id, from, to }) {
    if (!isNonEmptyString(id)) {
      throw new Error("Wire id must be a non-empty string");
    }
    if (!from || !isNonEmptyString(from.nodeId) || !isNonEmptyString(from.portId)) {
      throw new Error("Wire from must be {nodeId, portId} with non-empty strings");
    }
    if (!to || !isNonEmptyString(to.nodeId) || !isNonEmptyString(to.portId)) {
      throw new Error("Wire to must be {nodeId, portId} with non-empty strings");
    }

    this.id = id;
    this.from = { nodeId: from.nodeId, portId: from.portId };
    this.to = { nodeId: to.nodeId, portId: to.portId };
  }
}
