function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export function rectContainsPoint(rect, point) {
  if (
    !rect ||
    !isFiniteNumber(rect.x) ||
    !isFiniteNumber(rect.y) ||
    !isFiniteNumber(rect.width) ||
    !isFiniteNumber(rect.height)
  ) {
    throw new Error("rect must be {x,y,width,height} with finite numbers");
  }
  if (!point || !isFiniteNumber(point.x) || !isFiniteNumber(point.y)) {
    throw new Error("point must be {x,y} with finite numbers");
  }

  return (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  );
}
