import { snapToGrid } from "../palette/drop-math.js";

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export function computeResizeDeltaWorld(cursorWorld, startCursorWorld) {
  if (!cursorWorld || !isFiniteNumber(cursorWorld.x) || !isFiniteNumber(cursorWorld.y)) {
    throw new Error("cursorWorld must be {x,y} finite numbers");
  }
  if (
    !startCursorWorld ||
    !isFiniteNumber(startCursorWorld.x) ||
    !isFiniteNumber(startCursorWorld.y)
  ) {
    throw new Error("startCursorWorld must be {x,y} finite numbers");
  }

  return {
    dx: cursorWorld.x - startCursorWorld.x,
    dy: cursorWorld.y - startCursorWorld.y,
  };
}

export function clampSizeWorld(sizeWorld, { minWidth, minHeight } = {}) {
  if (!sizeWorld || !isFiniteNumber(sizeWorld.width) || !isFiniteNumber(sizeWorld.height)) {
    throw new Error("sizeWorld must be {width,height} finite numbers");
  }

  const mw = isFiniteNumber(minWidth) ? minWidth : 1;
  const mh = isFiniteNumber(minHeight) ? minHeight : 1;

  return {
    width: Math.max(mw, sizeWorld.width),
    height: Math.max(mh, sizeWorld.height),
  };
}

export function computeResizedSizeWorld(startSizeWorld, deltaWorld) {
  if (
    !startSizeWorld ||
    !isFiniteNumber(startSizeWorld.width) ||
    !isFiniteNumber(startSizeWorld.height)
  ) {
    throw new Error("startSizeWorld must be {width,height} finite numbers");
  }
  if (!deltaWorld || !isFiniteNumber(deltaWorld.dx) || !isFiniteNumber(deltaWorld.dy)) {
    throw new Error("deltaWorld must be {dx,dy} finite numbers");
  }

  return {
    width: startSizeWorld.width + deltaWorld.dx,
    height: startSizeWorld.height + deltaWorld.dy,
  };
}

export function snapSizeToGrid(sizeWorld, gridSize) {
  if (!sizeWorld || !isFiniteNumber(sizeWorld.width) || !isFiniteNumber(sizeWorld.height)) {
    throw new Error("sizeWorld must be {width,height} finite numbers");
  }

  return {
    width: snapToGrid(sizeWorld.width, gridSize),
    height: snapToGrid(sizeWorld.height, gridSize),
  };
}
