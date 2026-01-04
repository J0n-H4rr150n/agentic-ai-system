function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function assertBounds(bounds) {
  if (
    !bounds ||
    !isFiniteNumber(bounds.left) ||
    !isFiniteNumber(bounds.top) ||
    !isFiniteNumber(bounds.right) ||
    !isFiniteNumber(bounds.bottom)
  ) {
    throw new Error("bounds must be {left, top, right, bottom} numbers");
  }
}

export function getGridLinePositions(bounds, gridSize) {
  assertBounds(bounds);
  if (!isFiniteNumber(gridSize) || gridSize <= 0) {
    throw new Error("gridSize must be a positive number");
  }

  const startX = Math.floor(bounds.left / gridSize) * gridSize;
  const endX = Math.ceil(bounds.right / gridSize) * gridSize;
  const startY = Math.floor(bounds.top / gridSize) * gridSize;
  const endY = Math.ceil(bounds.bottom / gridSize) * gridSize;

  const vertical = [];
  for (let x = startX; x <= endX; x += gridSize) {
    vertical.push(x);
  }

  const horizontal = [];
  for (let y = startY; y <= endY; y += gridSize) {
    horizontal.push(y);
  }

  return { vertical, horizontal };
}
