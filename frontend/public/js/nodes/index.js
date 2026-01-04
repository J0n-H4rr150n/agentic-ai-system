import { BaseNode } from "./base.js";
import { ContainerNode } from "./container.js";
import { createId } from "../utils/id.js";
import { getPortHitAtWorldPoint } from "./port.js";
import { findContainingContainerId } from "./container-math.js";

function isContainerNode(node) {
  return node?.type === "container";
}

export class NodeManager {
  constructor() {
    this._nodes = [];
  }

  clear() {
    this._nodes = [];
  }

  add(node) {
    this._nodes.push(node);
  }

  addFromPalette({ type, title, position }) {
    const id = createId(`node-${type}`);
    let node;

    if (type === "container") {
      node = new ContainerNode({
        id,
        title,
        position,
        size: { width: 420, height: 280 },
      });
      // Keep containers behind regular nodes.
      this._nodes.unshift(node);
      return node;
    }

    node = new BaseNode({
      id,
      type,
      title,
      position,
    });
    this.add(node);
    this.updateParentForNode(node);
    return node;
  }

  getNodes() {
    return this._nodes;
  }

  getContainers() {
    return this._nodes.filter((n) => isContainerNode(n));
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

  updateParentForNode(node) {
    if (!node) {
      return;
    }

    const nodeId = node.id;
    if (typeof nodeId !== "string" || !nodeId) {
      return;
    }

    const containers = this.getContainers()
      .filter((c) => c.id !== nodeId)
      .map((c) => ({ id: c.id, boundsWorld: c.getBoundsWorld() }));

    const containerId = findContainingContainerId({
      nodeBoundsWorld: node.getBoundsWorld(),
      containers,
    });

    node.parentId = containerId;
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
    if (isContainerNode(node)) {
      // Keep containers behind their contents.
      return;
    }
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
