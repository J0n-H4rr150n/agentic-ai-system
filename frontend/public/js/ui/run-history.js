function el(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function formatRunItemTitle(run) {
  const status = run?.status ? String(run.status) : "unknown";
  const runId = run?.run_id ? String(run.run_id) : "";
  const shortId = runId.length > 8 ? runId.slice(0, 8) : runId;
  return `${status} (${shortId || "?"})`;
}

function formatRunItemMeta(run) {
  const completedAt = run?.completed_at ? new Date(run.completed_at) : null;
  if (!completedAt || Number.isNaN(completedAt.getTime())) {
    return "";
  }
  return completedAt.toLocaleString();
}

/**
 * @param {{ rootEl: HTMLElement, runHistoryApi: { listRuns: Function }, storage?: Storage }} params
 */
export function createRunHistoryViewer({ rootEl, runHistoryApi, storage = typeof localStorage === "undefined" ? null : localStorage }) {
  if (!rootEl) {
    throw new Error("createRunHistoryViewer: rootEl is required");
  }
  if (!runHistoryApi || typeof runHistoryApi.listRuns !== "function") {
    throw new Error("createRunHistoryViewer: runHistoryApi.listRuns is required");
  }

  const title = el("h2", "run-history-title");
  title.textContent = "Run History";

  const hint = el("div", "run-history-hint muted");

  const list = el("div", "run-history-list");

  const wrap = el("div", "run-history-root");
  wrap.append(title, hint, list);
  rootEl.replaceChildren(wrap);

  let workflowId = null;

  function renderHint(text) {
    hint.textContent = text;
  }

  function renderRuns(runs) {
    list.replaceChildren();

    const items = Array.isArray(runs) ? runs : [];
    if (!items.length) {
      return;
    }

    for (const run of items) {
      const item = el("div", "run-history-item");
      const itemTitle = el("div", "run-history-item-title");
      itemTitle.textContent = formatRunItemTitle(run);

      const itemMeta = el("div", "run-history-item-meta");
      const metaParts = [];
      const meta = formatRunItemMeta(run);
      if (meta) metaParts.push(meta);
      if (run?.error) metaParts.push(String(run.error));
      itemMeta.textContent = metaParts.join(" • ");

      item.append(itemTitle, itemMeta);
      list.append(item);
    }
  }

  async function refresh() {
    if (!workflowId) {
      renderHint("Save a workflow to see its past runs.");
      renderRuns([]);
      return;
    }

    renderHint(`Workflow: ${workflowId}`);

    try {
      const result = await runHistoryApi.listRuns({ workflowId, limit: 25 });
      renderRuns(result?.runs ?? []);
    } catch {
      renderHint(`Workflow: ${workflowId} (failed to load runs)`);
      renderRuns([]);
    }
  }

  function setWorkflowId(nextWorkflowId) {
    workflowId = typeof nextWorkflowId === "string" && nextWorkflowId ? nextWorkflowId : null;
    if (storage && workflowId) {
      try {
        storage.setItem("currentWorkflowId", workflowId);
      } catch {
        // Ignore storage errors.
      }
    }
    void refresh();
  }

  function loadFromStorage() {
    if (!storage) {
      return;
    }
    try {
      const stored = storage.getItem("currentWorkflowId");
      if (stored && typeof stored === "string") {
        workflowId = stored;
      }
    } catch {
      // Ignore storage errors.
    }
  }

  loadFromStorage();
  void refresh();

  return {
    refresh,
    setWorkflowId,
  };
}
