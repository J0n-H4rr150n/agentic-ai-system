import { BaseNode } from "./base.js";
import { createId } from "../utils/id.js";
import { getPortHitAtWorldPoint } from "./port.js";

export class NodeManager {
  constructor() {
    this._nodes = [];
  }

  add(node) {
    this._nodes.push(node);
  }

  addFromPalette({ type, title, position }) {
    const node = new BaseNode({
      id: createId(`node-${type}`),
      type,
      title,
      position,
    });
    this.add(node);
    return node;
  }

  getNodes() {
    return this._nodes;
  }

  getById(id) {
    return this._nodes.find((n) => n.id === id) ?? null;
  }

  getNodeAtWorldPoint(point) {
    // Iterate from top-most to bottom-most (last drawn on top).
    for (let i = this._nodes.length - 1; i >= 0; i -= 1) {
      const node = this._nodes[i];
      if (node.containsWorldPoint(point)) {
        return node;
      }
    }
    return null;
  }

  getPortAtWorldPoint(point, options = {}) {
    // Iterate from top-most to bottom-most so interactions prefer the top node.
    for (let i = this._nodes.length - 1; i >= 0; i -= 1) {
      const node = this._nodes[i];
      const hit = getPortHitAtWorldPoint({
        nodeBoundsWorld: node.getBoundsWorld(),
        ports: node.ports ?? [],
        worldPoint: point,
        hitRadiusWorld: options.hitRadiusWorld,
      });
      if (hit) {
        return { node, ...hit };
      }
    }
    return null;
  }

  bringToFront(node) {
    const index = this._nodes.indexOf(node);
    if (index === -1 || index === this._nodes.length - 1) {
      return;
    }
    this._nodes.splice(index, 1);
    this._nodes.push(node);
  }

  static createWithDemoNode() {
    const manager = new NodeManager();
    manager.add(
      new BaseNode({
        id: "demo-start",
        type: "start",
        title: "Start",
        position: { x: 80, y: 80 },
      }),
    );
    return manager;
  }
}
