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

export function zoomIn(viewport, { centerScreen, factor = 1.2 }) {
  const nextScale = clampScale(viewport.scale * factor);
  zoomAtScreenPoint(viewport, centerScreen, nextScale);
}

export function zoomOut(viewport, { centerScreen, factor = 1.2 }) {
  const nextScale = clampScale(viewport.scale / factor);
  zoomAtScreenPoint(viewport, centerScreen, nextScale);
}

export function fitToScreen(viewport, { nodes, canvasWidth, canvasHeight, padding = 60 }) {
  if (!nodes || nodes.length === 0) {
    // No nodes, reset to default view
    viewport.scale = 1;
    viewport.offsetX = 0;
    viewport.offsetY = 0;
    return;
  }

  // Calculate bounding box of all nodes
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const node of nodes) {
    const bounds = node.getBoundsWorld();
    minX = Math.min(minX, bounds.x);
    minY = Math.min(minY, bounds.y);
    maxX = Math.max(maxX, bounds.x + bounds.width);
    maxY = Math.max(maxY, bounds.y + bounds.height);
  }

  const contentWidth = maxX - minX;
  const contentHeight = maxY - minY;

  // Calculate scale to fit with padding
  const scaleX = (canvasWidth - padding * 2) / contentWidth;
  const scaleY = (canvasHeight - padding * 2) / contentHeight;
  const scale = clampScale(Math.min(scaleX, scaleY));

  // Center the content
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;

  viewport.scale = scale;
  viewport.offsetX = (canvasWidth / 2) / scale - centerX;
  viewport.offsetY = (canvasHeight / 2) / scale - centerY;
}
