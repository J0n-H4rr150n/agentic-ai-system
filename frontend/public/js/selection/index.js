import { screenToWorld } from "../canvas/viewport.js";
import {
  computeDragOffsetWorld,
  computeDraggedTopLeftWorld,
  snapPositionToGrid,
} from "./move-math.js";

export class SelectionManager {
  constructor({ canvas, viewport, nodeManager, gridSize }) {
    this.canvas = canvas;
    this.viewport = viewport;
    this.nodeManager = nodeManager;
    this.gridSize = gridSize;

    this._selectedNodeId = null;
    this._dragging = null;

    this._onMouseDown = (e) => {
      // Only handle left-click selection (panning is handled elsewhere).
      if (e.button !== 0) {
        return;
      }

      const world = this._eventToWorld(e);

      const portHit = this.nodeManager.getPortAtWorldPoint?.(world);
      if (portHit) {
        return;
      }

      const hit = this.nodeManager.getNodeAtWorldPoint(world);

      if (!hit) {
        this._selectedNodeId = null;
        this._dragging = null;
        return;
      }

      this._selectedNodeId = hit.id;
      this.nodeManager.bringToFront(hit);

      this._dragging = {
        nodeId: hit.id,
        offsetWorld: computeDragOffsetWorld(world, hit.position),
      };

      e.preventDefault();
    };

    this._onMouseMove = (e) => {
      if (!this._dragging) {
        return;
      }

      const node = this.nodeManager.getById(this._dragging.nodeId);
      if (!node) {
        this._dragging = null;
        return;
      }

      const world = this._eventToWorld(e);
      node.position = computeDraggedTopLeftWorld(world, this._dragging.offsetWorld);
    };

    this._onMouseUp = () => {
      if (!this._dragging) {
        return;
      }

      const node = this.nodeManager.getById(this._dragging.nodeId);
      this._dragging = null;

      if (!node) {
        return;
      }

      node.position = snapPositionToGrid(node.position, this.gridSize);
    };
  }

  getSelectedNodeId() {
    return this._selectedNodeId;
  }

  attach() {
    this.canvas.addEventListener("mousedown", this._onMouseDown);
    window.addEventListener("mousemove", this._onMouseMove);
    window.addEventListener("mouseup", this._onMouseUp);
  }

  detach() {
    this.canvas.removeEventListener("mousedown", this._onMouseDown);
    window.removeEventListener("mousemove", this._onMouseMove);
    window.removeEventListener("mouseup", this._onMouseUp);
  }

  _eventToWorld(e) {
    const rect = this.canvas.getBoundingClientRect();
    const screen = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
    return screenToWorld(screen, this.viewport);
  }
}
