import { BaseNode } from "./base.js";
import { worldToScreen } from "../canvas/viewport.js";

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

    ctx.restore();
  }
}
