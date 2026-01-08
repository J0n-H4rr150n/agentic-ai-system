import { createId } from "../utils/id.js";
import { computePortCentersWorld, PORT_KIND } from "../nodes/port.js";
import { Wire } from "./wire.js";
import { computeCubicBezierControlPoints } from "./bezier.js";
import { distanceToBezierCurve } from "./bezier-distance.js";

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

  /**
   * Find wire at world coordinates with threshold
   * @param {number} x - World x coordinate
   * @param {number} y - World y coordinate
   * @param {object} nodeManager - NodeManager instance to resolve endpoints
   * @param {number} threshold - Maximum distance to consider (pixels)
   * @returns {Wire|null} - Wire if found within threshold, null otherwise
   */
  getWireAtPoint({ x, y, nodeManager, threshold = 10 }) {
    const point = { x, y };

    for (const wire of this._wires) {
      // Get start and end nodes
      const fromNode = nodeManager.getNodeById(wire.from.nodeId);
      const toNode = nodeManager.getNodeById(wire.to.nodeId);

      if (!fromNode || !toNode) continue;

      // Resolve world coordinates of wire endpoints
      const startWorld = this.resolveEndpointWorld({ node: fromNode, portId: wire.from.portId });
      const endWorld = this.resolveEndpointWorld({ node: toNode, portId: wire.to.portId });

      if (!startWorld || !endWorld) continue;

      // Compute bezier control points
      const { c1World, c2World } = computeCubicBezierControlPoints({ startWorld, endWorld });

      // Calculate distance from point to curve
      const dist = distanceToBezierCurve({
        point,
        start: startWorld,
        c1: c1World,
        c2: c2World,
        end: endWorld,
      });

      if (dist <= threshold) {
        return wire;
      }
    }

    return null;
  }

  /**
   * Remove wire by ID
   * @param {string} wireId - ID of wire to remove
   * @returns {boolean} - true if wire was removed, false if not found
   */
  removeWire(wireId) {
    const index = this._wires.findIndex(w => w.id === wireId);
    if (index !== -1) {
      this._wires.splice(index, 1);
      return true;
    }
    return false;
  }
}
