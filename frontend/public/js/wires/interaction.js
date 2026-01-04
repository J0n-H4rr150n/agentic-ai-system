import { screenToWorld } from "../canvas/viewport.js";
import { PORT_KIND } from "../nodes/port.js";

export class WireInteractionManager {
  constructor({ canvas, viewport, nodeManager, wireManager }) {
    this.canvas = canvas;
    this.viewport = viewport;
    this.nodeManager = nodeManager;
    this.wireManager = wireManager;

    this._dragging = null;

    this._onMouseDown = (e) => {
      if (e.button !== 0) {
        return;
      }

      const world = this._eventToWorld(e);
      const hit = this.nodeManager.getPortAtWorldPoint(world);

      if (!hit) {
        return;
      }

      // Only start a wire from an output port.
      if (hit.kind !== PORT_KIND.OUTPUT) {
        return;
      }

      this._dragging = {
        from: { nodeId: hit.node.id, portId: hit.port.id },
        startWorld: hit.centerWorld,
        endWorld: world,
      };

      e.preventDefault();
    };

    this._onMouseMove = (e) => {
      if (!this._dragging) {
        return;
      }
      this._dragging.endWorld = this._eventToWorld(e);
    };

    this._onMouseUp = (e) => {
      if (!this._dragging) {
        return;
      }

      const drag = this._dragging;
      this._dragging = null;

      const world = this._eventToWorld(e);
      const hit = this.nodeManager.getPortAtWorldPoint(world);

      if (!hit) {
        return;
      }

      const fromNode = this.nodeManager.getById(drag.from.nodeId);
      const toNode = hit.node;

      if (!fromNode || !toNode) {
        return;
      }

      const fromPortInfo = {
        node: fromNode,
        port: fromNode.ports?.find((p) => p.id === drag.from.portId) ?? null,
        kind: PORT_KIND.OUTPUT,
      };

      const toPortInfo = {
        node: toNode,
        port: hit.port,
        kind: hit.kind,
      };

      // Validate output -> input only.
      if (!this.wireManager.isValidConnection({ fromPortInfo, toPortInfo })) {
        return;
      }

      this.wireManager.createWire({
        from: drag.from,
        to: { nodeId: toNode.id, portId: hit.port.id },
      });
    };
  }

  getPreviewWire() {
    if (!this._dragging) {
      return null;
    }
    return {
      startWorld: this._dragging.startWorld,
      endWorld: this._dragging.endWorld,
    };
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
