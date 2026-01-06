import { BaseNode } from "./base.js";
import { worldToScreen } from "../canvas/viewport.js";
import { rectContainsPoint } from "../utils/geometry.js";

export const CONTAINER_RESIZE_HANDLE_SIZE_WORLD = 16;

export class ContainerNode extends BaseNode {
  constructor({ id, title, position, size, config } = {}) {
    super({
      id,
      type: "container",
      title: title ?? "Container",
      position,
      size,
      ports: [],
      config,
    });

    this.parentId = null;
  }

  render(ctx, viewport, options = {}) {
    const topLeft = worldToScreen(this.position, viewport);
    const width = this.size.width * viewport.scale;
    const height = this.size.height * viewport.scale;

    ctx.save();
    ctx.translate(topLeft.x, topLeft.y);

    ctx.fillStyle = "#ffffff";
    ctx.globalAlpha = 0.6;
    ctx.strokeStyle = options.selected ? "#0f172a" : "#cbd5e1";
    ctx.lineWidth = options.selected ? 2 : 1;
    ctx.setLineDash([6 * viewport.scale, 4 * viewport.scale]);

    ctx.beginPath();
    ctx.rect(0, 0, width, height);
    ctx.fill();
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.globalAlpha = 1;

    ctx.fillStyle = "#0f172a";
    ctx.font = `${12 * viewport.scale}px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`;
    ctx.textBaseline = "top";
    ctx.fillText(this.title, 10 * viewport.scale, 10 * viewport.scale);

    if (options.selected) {
      const handleSize = CONTAINER_RESIZE_HANDLE_SIZE_WORLD * viewport.scale;
      const pad = 4 * viewport.scale;
      ctx.fillStyle = "#ffffff";
      ctx.strokeStyle = "#0f172a";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.rect(width - handleSize - pad, height - handleSize - pad, handleSize, handleSize);
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }

  getResizeHandleBoundsWorld({ sizeWorld } = {}) {
    const s = typeof sizeWorld === "number" && Number.isFinite(sizeWorld)
      ? sizeWorld
      : CONTAINER_RESIZE_HANDLE_SIZE_WORLD;

    return {
      x: this.position.x + this.size.width - s,
      y: this.position.y + this.size.height - s,
      width: s,
      height: s,
    };
  }

  isResizeHandleHit(worldPoint, options = {}) {
    const bounds = this.getResizeHandleBoundsWorld({ sizeWorld: options.sizeWorld });
    return rectContainsPoint(bounds, worldPoint);
  }
}
