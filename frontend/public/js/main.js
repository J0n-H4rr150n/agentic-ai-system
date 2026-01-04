import { CanvasManager } from "./canvas/index.js";
import { PaletteManager } from "./palette/index.js";
import { PALETTE_CATEGORIES } from "./palette/categories.js";
import { PaletteDragDropHandler } from "./palette/drag.js";
import { serializeGraph, stringifyGraph } from "./graph/serializer.js";
import { createRunApi } from "./api/run.js";
import { createRunController } from "./ui/run-controls.js";
import { createRunStatusIndicator, RUN_STATUSES } from "./ui/status.js";

function requireElementById(id) {
  const element = document.getElementById(id);
  if (!element) {
    throw new Error(`Missing element #${id}`);
  }
  return element;
}

function init() {
  const paletteRoot = requireElementById("paletteRoot");
  const exportJsonButton = requireElementById("exportJsonButton");

  const runButton = requireElementById("runButton");
  const runStatus = requireElementById("runStatus");

  const canvas = requireElementById("agentCanvas");
  const host = requireElementById("canvasHost");

  const palette = new PaletteManager({
    root: paletteRoot,
    categories: PALETTE_CATEGORIES,
  });
  palette.render();

  // CanvasManager owns resize/render loop.
  // Pan/zoom comes in S004.
  const manager = new CanvasManager({ canvas, host });
  manager.start();

  exportJsonButton.addEventListener("click", () => {
    const graph = serializeGraph({
      nodeManager: manager.nodeManager,
      wireManager: manager.wireManager,
    });
    downloadTextFile("graph.json", stringifyGraph(graph));
  });

  const statusIndicator = createRunStatusIndicator({ element: runStatus });
  const runApi = createRunApi();
  const controller = createRunController({
    runApi,
    getGraph: () =>
      serializeGraph({
        nodeManager: manager.nodeManager,
        wireManager: manager.wireManager,
      }),
    onStatus: (status, details) => {
      statusIndicator.setStatus(status, details);
      runButton.disabled = status === RUN_STATUSES.RUNNING;
    },
  });

  runButton.addEventListener("click", async () => {
    await controller.runOnce();
  });

  const dragDrop = new PaletteDragDropHandler({
    paletteRoot,
    canvas,
    canvasManager: manager,
  });
  dragDrop.attach();
}

function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  // Release the blob URL on next tick.
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
