import { drawGrid } from "./grid.js";
import { worldToScreen } from "./viewport.js";
import { computeCubicBezierControlPoints } from "../wires/bezier.js";

export function createRenderer({ ctx, viewport, nodeManager, wireManager, wireInteraction }) {
  return {
    render({ canvasWidth, canvasHeight }) {
      ctx.clearRect(0, 0, canvasWidth, canvasHeight);
      drawGrid(ctx, { canvasWidth, canvasHeight, viewport, gridSize: 10 });

      if (wireManager && nodeManager) {
        const selectedWireId = wireManager.getSelectedWireId?.() ?? null;

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

          // Apply selection styling
          const isSelected = wire.id === selectedWireId;
          ctx.save();
          ctx.strokeStyle = isSelected ? "#3b82f6" : "#cbd5e1";
          ctx.lineWidth = isSelected ? 3 : 2;
          drawBezierWorld(ctx, viewport, { startWorld, endWorld });
          ctx.restore();
        }

        const preview = wireInteraction?.getPreviewWire?.() ?? null;
        if (preview) {
          ctx.save();
          ctx.strokeStyle = "#cbd5e1";
          ctx.lineWidth = 2;
          drawBezierWorld(ctx, viewport, preview);
          ctx.restore();
        }
      }

      if (nodeManager) {
        const selectedId = nodeManager.getSelectedNodeId?.() ?? null;
        const highlightedContainerId = nodeManager.getHighlightedContainerId?.() ?? null;
        for (const node of nodeManager.getNodes()) {
          node.render(ctx, viewport, {
            selected: node.id === selectedId,
            highlighted: node.id === highlightedContainerId,
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
