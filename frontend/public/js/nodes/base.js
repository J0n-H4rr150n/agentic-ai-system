import { worldToScreen } from "../canvas/viewport.js";
import { rectContainsPoint } from "../utils/geometry.js";
import {
  computePortCentersWorld,
  createDefaultPortsForNodeType,
  PORT_RADIUS_WORLD,
} from "./port.js";

export class BaseNode {
  constructor({ id, type, title, position, size, ports, config }) {
    if (!id || typeof id !== "string") {
      throw new Error("id must be a non-empty string");
    }
    if (!type || typeof type !== "string") {
      throw new Error("type must be a non-empty string");
    }

    this.id = id;
    this.type = type;
    this.title = title ?? type;

    this.position = {
      x: position?.x ?? 0,
      y: position?.y ?? 0,
    };

    this.size = {
      width: size?.width ?? 180,
      height: size?.height ?? 72,
    };

    this.ports = ports ?? createDefaultPortsForNodeType({ nodeId: this.id, type: this.type });

    this.config = config && typeof config === "object" && !Array.isArray(config) ? config : {};

    // Optional HITL interrupt configuration, serialized to the backend graph.
    // Shape: { before: boolean, after: boolean, reason?: string }
    this.interrupt = null;

    // UI-only grouping metadata.
    this.parentId = null;
  }

  getBoundsWorld() {
    return {
      x: this.position.x,
      y: this.position.y,
      width: this.size.width,
      height: this.size.height,
    };
  }

  containsWorldPoint(point) {
    return rectContainsPoint(this.getBoundsWorld(), point);
  }

  render(ctx, viewport, options = {}) {
    const topLeft = worldToScreen(this.position, viewport);
    const width = this.size.width * viewport.scale;
    const height = this.size.height * viewport.scale;

    ctx.save();
    ctx.translate(topLeft.x, topLeft.y);

    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = options.selected ? "#0f172a" : "#cbd5e1";
    ctx.lineWidth = options.selected ? 2 : 1;

    ctx.beginPath();
    ctx.rect(0, 0, width, height);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#0f172a";
    ctx.font = `${12 * viewport.scale}px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`;
    ctx.textBaseline = "top";
    ctx.fillText(this.title, 10 * viewport.scale, 10 * viewport.scale);

    const ports = computePortCentersWorld({
      nodeBoundsWorld: this.getBoundsWorld(),
      ports: this.ports,
    });

    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = options.selected ? "#0f172a" : "#cbd5e1";
    ctx.lineWidth = 1;

    const r = PORT_RADIUS_WORLD * viewport.scale;
    for (const info of ports) {
      const centerScreen = worldToScreen(info.centerWorld, viewport);
      const localX = centerScreen.x - topLeft.x;
      const localY = centerScreen.y - topLeft.y;

      ctx.beginPath();
      ctx.arc(localX, localY, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }
}
