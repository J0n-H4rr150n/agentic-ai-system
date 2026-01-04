export function createViewport() {
  return {
    offsetX: 0,
    offsetY: 0,
    scale: 1,
  };
}

export function clampScale(scale) {
  const min = 0.25;
  const max = 4;
  if (!Number.isFinite(scale)) {
    throw new Error("scale must be a finite number");
  }
  return Math.min(max, Math.max(min, scale));
}

export function panByScreenDelta(viewport, { dx, dy }) {
  if (!Number.isFinite(dx) || !Number.isFinite(dy)) {
    throw new Error("dx/dy must be finite numbers");
  }
  viewport.offsetX += dx / viewport.scale;
  viewport.offsetY += dy / viewport.scale;
}

export function zoomAtScreenPoint(viewport, screenPoint, nextScale) {
  const clamped = clampScale(nextScale);

  const worldBefore = screenToWorld(screenPoint, viewport);
  viewport.scale = clamped;

  // Maintain the same world point under the cursor.
  viewport.offsetX = screenPoint.x / viewport.scale - worldBefore.x;
  viewport.offsetY = screenPoint.y / viewport.scale - worldBefore.y;
}

export function worldToScreen(point, viewport) {
  return {
    x: (point.x + viewport.offsetX) * viewport.scale,
    y: (point.y + viewport.offsetY) * viewport.scale,
  };
}

export function screenToWorld(point, viewport) {
  return {
    x: point.x / viewport.scale - viewport.offsetX,
    y: point.y / viewport.scale - viewport.offsetY,
  };
}
