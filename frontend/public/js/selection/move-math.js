import { snapToGrid } from "../palette/drop-math.js";

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export function computeDragOffsetWorld(cursorWorld, nodePositionWorld) {
  if (!cursorWorld || !isFiniteNumber(cursorWorld.x) || !isFiniteNumber(cursorWorld.y)) {
    throw new Error("cursorWorld must be {x,y} finite numbers");
  }
  if (
    !nodePositionWorld ||
    !isFiniteNumber(nodePositionWorld.x) ||
    !isFiniteNumber(nodePositionWorld.y)
  ) {
    throw new Error("nodePositionWorld must be {x,y} finite numbers");
  }

  return {
    x: cursorWorld.x - nodePositionWorld.x,
    y: cursorWorld.y - nodePositionWorld.y,
  };
}

export function computeDraggedTopLeftWorld(cursorWorld, dragOffsetWorld) {
  if (!cursorWorld || !isFiniteNumber(cursorWorld.x) || !isFiniteNumber(cursorWorld.y)) {
    throw new Error("cursorWorld must be {x,y} finite numbers");
  }
  if (
    !dragOffsetWorld ||
    !isFiniteNumber(dragOffsetWorld.x) ||
    !isFiniteNumber(dragOffsetWorld.y)
  ) {
    throw new Error("dragOffsetWorld must be {x,y} finite numbers");
  }

  return {
    x: cursorWorld.x - dragOffsetWorld.x,
    y: cursorWorld.y - dragOffsetWorld.y,
  };
}

export function snapPositionToGrid(positionWorld, gridSize) {
  if (!positionWorld || !isFiniteNumber(positionWorld.x) || !isFiniteNumber(positionWorld.y)) {
    throw new Error("positionWorld must be {x,y} finite numbers");
  }
  return {
    x: snapToGrid(positionWorld.x, gridSize),
    y: snapToGrid(positionWorld.y, gridSize),
  };
}
