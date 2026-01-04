import { CanvasManager } from "./canvas/index.js";
import { PaletteManager } from "./palette/index.js";
import { PALETTE_CATEGORIES } from "./palette/categories.js";
import { PaletteDragDropHandler } from "./palette/drag.js";
import { buildPaletteCategoriesWithSavedAgents } from "./palette/saved-agents.js";
import { serializeGraph, stringifyGraph } from "./graph/serializer.js";
import { createRunApi } from "./api/run.js";
import { createWorkflowApi } from "./api/workflow.js";
import { createRunController } from "./ui/run-controls.js";
import { createRunStatusIndicator, RUN_STATUSES } from "./ui/status.js";
import { createSaveAsNodeController } from "./ui/save-as-node.js";
import { createWorkflowStatusIndicator, WORKFLOW_SAVE_STATUSES } from "./ui/workflow-status.js";
import { createExecutionTraceViewer } from "./ui/trace/index.js";
import { createRunHistoryApi } from "./api/run-history.js";
import { createRunHistoryViewer } from "./ui/run-history.js";
import { loadPersistedRun } from "./ui/run-history-loader.js";

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
  const saveAsNodeButton = requireElementById("saveAsNodeButton");
  const workflowStatus = requireElementById("workflowStatus");
  const traceRoot = requireElementById("traceRoot");
  const runHistoryRoot = requireElementById("runHistoryRoot");

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
  const workflowStatusIndicator = createWorkflowStatusIndicator({ element: workflowStatus });
  const traceViewer = createExecutionTraceViewer({ rootEl: traceRoot });
  const runApi = createRunApi();
  const workflowApi = createWorkflowApi();
  const runHistoryApi = createRunHistoryApi();
  const runHistoryViewer = createRunHistoryViewer({
    rootEl: runHistoryRoot,
    runHistoryApi,
    onRunSelected: async (runId) => {
      try {
        const loaded = await loadPersistedRun({ runId, runHistoryApi, workflowApi });

        traceViewer.clear();
        traceViewer.setGraph(loaded.graph);
        for (const step of loaded.trace) {
          traceViewer.appendStep(step);
        }

        statusIndicator.setStatus(loaded.status, { runId: loaded.runId, error: loaded.error });
      } catch {
        // Ignore selection errors in MVP.
      }
    },
    onReplayRequested: async (runId) => {
      try {
        // Load graph metadata for display.
        const detail = await runHistoryApi.getRun(runId);
        const workflowId = detail?.workflow_id ?? null;
        const wf = workflowId ? await workflowApi.getWorkflow(workflowId) : null;
        const graph = wf?.graph ?? null;

        // Start a new run from the persisted checkpoint.
        const replayed = await runHistoryApi.replayRun(runId);
        const newRunId = replayed?.run_id;
        if (!newRunId) {
          return;
        }

        traceViewer.clear();
        traceViewer.setGraph(graph);
        statusIndicator.setStatus(RUN_STATUSES.RUNNING, { runId: newRunId, error: null });
        runButton.disabled = true;

        // Poll for trace growth and terminal status.
        let seen = 0;
        while (true) {
          const current = await runApi.getRun(newRunId);
          const status = current?.status ?? RUN_STATUSES.RUNNING;
          const error = current?.error ?? null;
          const trace = Array.isArray(current?.trace) ? current.trace : [];

          for (const step of trace.slice(seen)) {
            traceViewer.appendStep(step);
          }
          seen = trace.length;

          statusIndicator.setStatus(status, { runId: newRunId, error });
          if (status !== RUN_STATUSES.RUNNING) {
            runButton.disabled = false;
            runHistoryViewer.refresh();
            return;
          }

          await new Promise((r) => setTimeout(r, 250));
        }
      } catch {
        // Ignore replay errors in MVP.
      }
    },
  });

  // Load saved agents for display in the palette.
  workflowApi
    .listWorkflows()
    .then((result) => {
      const workflows = result?.workflows ?? [];
      palette.categories = buildPaletteCategoriesWithSavedAgents({
        categories: PALETTE_CATEGORIES,
        workflows,
      });
      palette.render();
    })
    .catch(() => {
      // Ignore listing errors in MVP; keep built-in palette.
    });
  const controller = createRunController({
    runApi,
    getGraph: () =>
      serializeGraph({
        nodeManager: manager.nodeManager,
        wireManager: manager.wireManager,
      }),
    getWorkflowId: () => {
      try {
        const v = localStorage.getItem("currentWorkflowId");
        return v && typeof v === "string" ? v : null;
      } catch {
        return null;
      }
    },
    onRunStart: (graph) => {
      traceViewer.clear();
      traceViewer.setGraph(graph);
    },
    onStep: (step) => {
      traceViewer.appendStep(step);
    },
    onStatus: (status, details) => {
      statusIndicator.setStatus(status, details);
      runButton.disabled = status === RUN_STATUSES.RUNNING;

      if (status !== RUN_STATUSES.RUNNING && status !== RUN_STATUSES.IDLE) {
        runHistoryViewer.refresh();
      }
    },
  });

  runButton.addEventListener("click", async () => {
    await controller.runOnce();
  });

  const saveAsNodeController = createSaveAsNodeController({
    workflowApi,
    getGraph: () =>
      serializeGraph({
        nodeManager: manager.nodeManager,
        wireManager: manager.wireManager,
      }),
    onStatus: (status, details) => {
      workflowStatusIndicator.setStatus(status, details);
      saveAsNodeButton.disabled = status === WORKFLOW_SAVE_STATUSES.SAVING;

      if (status === WORKFLOW_SAVE_STATUSES.SAVED && details?.workflowId) {
        runHistoryViewer.setWorkflowId(details.workflowId);
      }
    },
  });

  saveAsNodeButton.addEventListener("click", async () => {
    await saveAsNodeController.save();
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
