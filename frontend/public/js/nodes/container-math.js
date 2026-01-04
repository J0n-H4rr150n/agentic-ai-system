import { rectContainsPoint } from "../utils/geometry.js";

function isFiniteNumber(n) {
  return typeof n === "number" && Number.isFinite(n);
}

function assertRect(rect, name) {
  if (
    !rect ||
    !isFiniteNumber(rect.x) ||
    !isFiniteNumber(rect.y) ||
    !isFiniteNumber(rect.width) ||
    !isFiniteNumber(rect.height)
  ) {
    throw new Error(`${name} must be {x,y,width,height} with finite numbers`);
  }
}

export function getRectCenter(rect) {
  assertRect(rect, "rect");
  return {
    x: rect.x + rect.width / 2,
    y: rect.y + rect.height / 2,
  };
}

export function rectContainsRect(outer, inner) {
  assertRect(outer, "outer");
  assertRect(inner, "inner");

  const corners = [
    { x: inner.x, y: inner.y },
    { x: inner.x + inner.width, y: inner.y },
    { x: inner.x, y: inner.y + inner.height },
    { x: inner.x + inner.width, y: inner.y + inner.height },
  ];

  for (const corner of corners) {
    if (!rectContainsPoint(outer, corner)) {
      return false;
    }
  }
  return true;
}

/**
 * Choose the smallest container that contains the node.
 *
 * @param {{ nodeBoundsWorld: {x:number,y:number,width:number,height:number}, containers: Array<{id:string, boundsWorld:{x:number,y:number,width:number,height:number}}> }} params
 */
export function findContainingContainerId({ nodeBoundsWorld, containers }) {
  assertRect(nodeBoundsWorld, "nodeBoundsWorld");

  const list = Array.isArray(containers) ? containers : [];
  let best = null;

  for (const c of list) {
    const id = c?.id;
    const bounds = c?.boundsWorld;
    if (typeof id !== "string" || !id) {
      continue;
    }
    if (!bounds) {
      continue;
    }

    if (!rectContainsRect(bounds, nodeBoundsWorld)) {
      continue;
    }

    const area = bounds.width * bounds.height;
    if (!best || area < best.area) {
      best = { id, area };
    }
  }

  return best ? best.id : null;
}
