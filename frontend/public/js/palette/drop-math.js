import { screenToWorld } from "../canvas/viewport.js";

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export function snapToGrid(value, gridSize) {
  if (!isFiniteNumber(value) || !isFiniteNumber(gridSize) || gridSize <= 0) {
    throw new Error("value and gridSize must be finite numbers; gridSize > 0");
  }
  const snapped = Math.round(value / gridSize) * gridSize;
  return Object.is(snapped, -0) ? 0 : snapped;
}

export function computeDropTopLeftWorld({
  screenPoint,
  viewport,
  nodeSize,
  gridSize,
}) {
  if (!screenPoint || !isFiniteNumber(screenPoint.x) || !isFiniteNumber(screenPoint.y)) {
    throw new Error("screenPoint must be {x,y} finite numbers");
  }
  if (!viewport || !isFiniteNumber(viewport.scale)) {
    throw new Error("viewport is required");
  }
  if (!nodeSize || !isFiniteNumber(nodeSize.width) || !isFiniteNumber(nodeSize.height)) {
    throw new Error("nodeSize must be {width,height} finite numbers");
  }

  const worldAtCursor = screenToWorld(screenPoint, viewport);
  const rawTopLeft = {
    x: worldAtCursor.x - nodeSize.width / 2,
    y: worldAtCursor.y - nodeSize.height / 2,
  };

  return {
    x: snapToGrid(rawTopLeft.x, gridSize),
    y: snapToGrid(rawTopLeft.y, gridSize),
  };
}
