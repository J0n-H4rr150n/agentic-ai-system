import { drawGrid } from "./grid.js";
import { worldToScreen } from "./viewport.js";
import { computeCubicBezierControlPoints } from "../wires/bezier.js";

export function createRenderer({ ctx, viewport, nodeManager, wireManager, wireInteraction }) {
  return {
    render({ canvasWidth, canvasHeight }) {
      ctx.clearRect(0, 0, canvasWidth, canvasHeight);
      drawGrid(ctx, { canvasWidth, canvasHeight, viewport, gridSize: 10 });

      if (wireManager && nodeManager) {
        ctx.save();
        ctx.strokeStyle = "#cbd5e1";
        ctx.lineWidth = 2;

        for (const wire of wireManager.getWires()) {
          const fromNode = nodeManager.getById(wire.from.nodeId);
          const toNode = nodeManager.getById(wire.to.nodeId);
          if (!fromNode || !toNode) {
            continue;
          }

          const startWorld = wireManager.resolveEndpointWorld({
            node: fromNode,
            portId: wire.from.portId,
          });
          const endWorld = wireManager.resolveEndpointWorld({
            node: toNode,
            portId: wire.to.portId,
          });

          if (!startWorld || !endWorld) {
            continue;
          }

          drawBezierWorld(ctx, viewport, { startWorld, endWorld });
        }

        const preview = wireInteraction?.getPreviewWire?.() ?? null;
        if (preview) {
          drawBezierWorld(ctx, viewport, preview);
        }

        ctx.restore();
      }

      if (nodeManager) {
        const selectedId = nodeManager.getSelectedNodeId?.() ?? null;
        for (const node of nodeManager.getNodes()) {
          node.render(ctx, viewport, {
            selected: node.id === selectedId,
            nodeManager: nodeManager
          });
        }
      }
    },
  };
}

function drawBezierWorld(ctx, viewport, { startWorld, endWorld }) {
  const { c1World, c2World } = computeCubicBezierControlPoints({ startWorld, endWorld });

  const start = worldToScreen(startWorld, viewport);
  const end = worldToScreen(endWorld, viewport);
  const c1 = worldToScreen(c1World, viewport);
  const c2 = worldToScreen(c2World, viewport);

  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.bezierCurveTo(c1.x, c1.y, c2.x, c2.y, end.x, end.y);
  ctx.stroke();
}
