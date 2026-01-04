import { createStepElement } from "./step.js";

function el(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function buildGraphIndex(graph) {
  if (!graph || typeof graph !== "object") {
    return null;
  }

  const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
  const index = new Map();
  for (const node of nodes) {
    if (!node || typeof node !== "object") continue;
    if (!node.id) continue;
    index.set(node.id, {
      title: node.title || null,
      type: node.type || null,
    });
  }

  return index;
}

export function createExecutionTraceViewer({ rootEl }) {
  if (!rootEl) {
    throw new Error("createExecutionTraceViewer: rootEl is required");
  }

  let graphIndex = null;

  const list = el("div");
  list.className = "trace-list";
  rootEl.replaceChildren(list);

  function clear() {
    list.replaceChildren();
  }

  function setGraph(graph) {
    graphIndex = buildGraphIndex(graph);
  }

  function appendStep(step) {
    const stepEl = createStepElement({ step, graphIndex });
    list.append(stepEl);

    // Auto-scroll while running (always enabled per story spec).
    queueMicrotask(() => {
      rootEl.scrollTo({ top: rootEl.scrollHeight });
    });
  }

  return {
    clear,
    setGraph,
    appendStep,
  };
}
