import { panByScreenDelta, screenToWorld } from "../canvas/viewport.js";
import {
  computeDragOffsetWorld,
  computeDraggedTopLeftWorld,
  snapPositionToGrid,
} from "./move-math.js";
import {
  clampSizeWorld,
  computeResizeDeltaWorld,
  computeResizedSizeWorld,
  snapSizeToGrid,
} from "./resize-math.js";

export class SelectionManager {
  constructor({ canvas, viewport, nodeManager, gridSize }) {
    this.canvas = canvas;
    this.viewport = viewport;
    this.nodeManager = nodeManager;
    this.gridSize = gridSize;

    this._selectedNodeId = null;
    this._onSelectionChanged = null;
    this._dragging = null;
    this._resizing = null;
    this._panning = null;

    this._setSelectedNodeId = (nextId) => {
      const normalized = nextId ?? null;
      if (normalized === this._selectedNodeId) {
        return;
      }
      this._selectedNodeId = normalized;
      if (typeof this._onSelectionChanged === "function") {
        this._onSelectionChanged(this._selectedNodeId);
      }
    };

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
        this._setSelectedNodeId(null);
        this._dragging = null;
        this._resizing = null;

        // Standard canvas behavior: drag the background to pan.
        this._panning = { last: { x: e.clientX, y: e.clientY } };
        e.preventDefault();
        return;
      }

      this._setSelectedNodeId(hit.id);
      this.nodeManager.bringToFront(hit);

      this._panning = null;

      if (hit?.type === "container" && typeof hit.isResizeHandleHit === "function") {
        if (hit.isResizeHandleHit(world)) {
          this._dragging = null;
          this._resizing = {
            nodeId: hit.id,
            startCursorWorld: world,
            startSizeWorld: { width: hit.size.width, height: hit.size.height },
          };
          e.preventDefault();
          return;
        }
      }

      this._dragging = {
        nodeId: hit.id,
        offsetWorld: computeDragOffsetWorld(world, hit.position),
      };

      this._resizing = null;

      e.preventDefault();
    };

    this._onMouseMove = (e) => {
      if (this._panning) {
        const dx = e.clientX - this._panning.last.x;
        const dy = e.clientY - this._panning.last.y;
        this._panning.last = { x: e.clientX, y: e.clientY };
        panByScreenDelta(this.viewport, { dx, dy });
        return;
      }

      if (this._resizing) {
        const node = this.nodeManager.getById(this._resizing.nodeId);
        if (!node) {
          this._resizing = null;
          return;
        }

        const world = this._eventToWorld(e);
        const delta = computeResizeDeltaWorld(world, this._resizing.startCursorWorld);
        const next = computeResizedSizeWorld(this._resizing.startSizeWorld, delta);

        const min = node.type === "container" ? { minWidth: 120, minHeight: 80 } : { minWidth: 1, minHeight: 1 };
        const clamped = clampSizeWorld(next, min);
        node.size = clamped;
        return;
      }

      if (!this._dragging) {
        return;
      }

      const node = this.nodeManager.getById(this._dragging.nodeId);
      if (!node) {
        this._dragging = null;
        return;
      }

      const world = this._eventToWorld(e);
      const nextPosition = computeDraggedTopLeftWorld(world, this._dragging.offsetWorld);

      // If dragging a container, move children with it
      if (node.type === "container") {
        const dx = nextPosition.x - node.position.x;
        const dy = nextPosition.y - node.position.y;

        // Move container
        node.position = nextPosition;

        // Move all children by the same delta
        const children = this.nodeManager.getNodes().filter(n => n.parentId === node.id);
        for (const child of children) {
          child.position.x += dx;
          child.position.y += dy;
        }
      } else {
        node.position = nextPosition;
      }
    };

    this._onMouseUp = () => {
      if (this._panning) {
        this._panning = null;
        return;
      }

      if (this._resizing) {
        const node = this.nodeManager.getById(this._resizing.nodeId);
        this._resizing = null;
        if (!node) {
          return;
        }

        node.size = snapSizeToGrid(node.size, this.gridSize);

        // Resizing a container can affect containment relationships.
        const nodes = this.nodeManager.getNodes?.() ?? [];
        for (const n of nodes) {
          if (n?.type === "container") {
            continue;
          }
          this.nodeManager.updateParentForNode?.(n);
        }

        return;
      }

      if (this._dragging) {
        const node = this.nodeManager.getById(this._dragging.nodeId);
        this._dragging = null;

        if (!node) {
          return;
        }

        node.position = snapPositionToGrid(node.position, this.gridSize);
        this.nodeManager.updateParentForNode?.(node);
      }
    };
  }

  getSelectedNodeId() {
    return this._selectedNodeId;
  }

  setOnSelectionChanged(callback) {
    this._onSelectionChanged = callback;
  }

  clearSelection() {
    this._setSelectedNodeId(null);
    this._dragging = null;
    this._resizing = null;
    this._panning = null;
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
