import { createId } from "../utils/id.js";
import { computePortCentersWorld, PORT_KIND } from "../nodes/port.js";
import { Wire } from "./wire.js";

export class WireManager {
  constructor() {
    this._wires = [];
  }

  clear() {
    this._wires = [];
  }

  getWires() {
    return this._wires;
  }

  addWire(wire) {
    this._wires.push(wire);
  }

  createWire({ from, to }) {
    const wire = new Wire({ id: createId("wire"), from, to });
    this.addWire(wire);
    return wire;
  }

  resolveEndpointWorld({ node, portId }) {
    const ports = node.ports ?? [];
    const centers = computePortCentersWorld({ nodeBoundsWorld: node.getBoundsWorld(), ports });
    const match = centers.find((c) => c.port.id === portId);
    return match?.centerWorld ?? null;
  }

  isValidConnection({ fromPortInfo, toPortInfo }) {
    return WireManager.isValidConnection({ fromPortInfo, toPortInfo });
  }

  static isValidConnection({ fromPortInfo, toPortInfo }) {
    if (!fromPortInfo || !toPortInfo) {
      return false;
    }
    return fromPortInfo.kind === PORT_KIND.OUTPUT && toPortInfo.kind === PORT_KIND.INPUT;
  }
}
