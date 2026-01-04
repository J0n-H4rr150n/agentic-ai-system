import { getGridLinePositions } from "./grid-math.js";
import { screenToWorld, worldToScreen } from "./viewport.js";

export function drawGrid(ctx, { canvasWidth, canvasHeight, viewport, gridSize }) {
  const topLeftWorld = screenToWorld({ x: 0, y: 0 }, viewport);
  const bottomRightWorld = screenToWorld(
    { x: canvasWidth, y: canvasHeight },
    viewport,
  );

  const boundsWorld = {
    left: Math.min(topLeftWorld.x, bottomRightWorld.x),
    top: Math.min(topLeftWorld.y, bottomRightWorld.y),
    right: Math.max(topLeftWorld.x, bottomRightWorld.x),
    bottom: Math.max(topLeftWorld.y, bottomRightWorld.y),
  };

  const { vertical, horizontal } = getGridLinePositions(boundsWorld, gridSize);

  ctx.save();
  ctx.lineWidth = 1;
  ctx.strokeStyle = "#f1f5f9";

  ctx.beginPath();
  for (const x of vertical) {
    const sx = worldToScreen({ x, y: 0 }, viewport).x;
    ctx.moveTo(sx + 0.5, 0);
    ctx.lineTo(sx + 0.5, canvasHeight);
  }
  for (const y of horizontal) {
    const sy = worldToScreen({ x: 0, y }, viewport).y;
    ctx.moveTo(0, sy + 0.5);
    ctx.lineTo(canvasWidth, sy + 0.5);
  }
  ctx.stroke();

  ctx.restore();
}
