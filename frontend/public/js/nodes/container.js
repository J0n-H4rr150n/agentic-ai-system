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

    // Get child count if nodeManager is provided
    const childCount = options.nodeManager
      ? options.nodeManager.getNodes().filter(n => n.parentId === this.id).length
      : 0;
    const titleText = childCount > 0 ? `${this.title} (${childCount})` : this.title;

    // Determine visual state
    const isEmpty = childCount === 0;
    const isHighlighted = options.highlighted && !options.selected;
    const isSelected = options.selected;

    ctx.save();
    ctx.translate(topLeft.x, topLeft.y);

    // Background - semi-transparent blue
    ctx.fillStyle = "rgba(100, 150, 200, 0.08)";
    ctx.globalAlpha = isHighlighted ? 1 : (isEmpty ? 0.6 : 0.8);
    ctx.fillRect(0, 0, width, height);
    ctx.globalAlpha = 1;

    // Border - 4 distinct states
    if (isSelected) {
      // Selected: dark border, solid
      ctx.strokeStyle = "#0f172a";
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
    } else if (isHighlighted) {
      // Highlighted: blue accent border when child is selected
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 2;
      ctx.setLineDash([]);
    } else if (isEmpty) {
      // Empty: light gray, dashed
      ctx.strokeStyle = "#cbd5e1";
      ctx.lineWidth = 1;
      ctx.setLineDash([6 * viewport.scale, 4 * viewport.scale]);
    } else {
      // Populated: medium gray, solid
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 1;
      ctx.setLineDash([]);
    }

    ctx.beginPath();
    ctx.rect(0, 0, width, height);
    ctx.stroke();

    // Reset line dash
    ctx.setLineDash([]);

    // Title text
    ctx.fillStyle = "#0f172a";
    ctx.font = `${12 * viewport.scale}px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`;
    ctx.textBaseline = "top";
    ctx.fillText(titleText, 10 * viewport.scale, 10 * viewport.scale);

    // Resize handle (only when selected)
    if (isSelected) {
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
