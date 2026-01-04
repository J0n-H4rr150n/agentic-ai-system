function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function validatePoint(point, name) {
  if (!point || !isFiniteNumber(point.x) || !isFiniteNumber(point.y)) {
    throw new Error(`${name} must be {x,y} with finite numbers`);
  }
}

export function computeCubicBezierControlPoints({ startWorld, endWorld }) {
  validatePoint(startWorld, "startWorld");
  validatePoint(endWorld, "endWorld");

  const dx = Math.abs(endWorld.x - startWorld.x);
  const offsetX = Math.max(40, dx * 0.5);

  return {
    c1World: { x: startWorld.x + offsetX, y: startWorld.y },
    c2World: { x: endWorld.x - offsetX, y: endWorld.y },
  };
}
