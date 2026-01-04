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
 * @param {{
 *  rootEl: HTMLElement,
 *  runHistoryApi: { listRuns: Function },
 *  onRunSelected?: (runId: string) => void,
 *  onReplayRequested?: (runId: string) => void,
 *  storage?: Storage,
 * }} params
 */
export function createRunHistoryViewer({
  rootEl,
  runHistoryApi,
  onRunSelected,
  onReplayRequested,
  storage = typeof localStorage === "undefined" ? null : localStorage,
}) {
  if (!rootEl) {
    throw new Error("createRunHistoryViewer: rootEl is required");
  }
  if (!runHistoryApi || typeof runHistoryApi.listRuns !== "function") {
    throw new Error("createRunHistoryViewer: runHistoryApi.listRuns is required");
  }
  if (onRunSelected !== undefined && typeof onRunSelected !== "function") {
    throw new Error("createRunHistoryViewer: onRunSelected must be a function if provided");
  }
  if (onReplayRequested !== undefined && typeof onReplayRequested !== "function") {
    throw new Error("createRunHistoryViewer: onReplayRequested must be a function if provided");
  }

  const title = el("h2", "run-history-title");
  title.textContent = "Run History";

  const filters = el("div", "run-history-filters");

  const statusFilter = el("select", "run-history-filter");
  statusFilter.setAttribute("aria-label", "Filter by status");
  statusFilter.append(
    new Option("All statuses", ""),
    new Option("Completed", "completed"),
    new Option("Failed", "failed"),
    new Option("Cancelled", "cancelled"),
  );

  const nodeTypeFilter = el("input", "run-history-filter");
  nodeTypeFilter.type = "text";
  nodeTypeFilter.placeholder = "Node type…";
  nodeTypeFilter.setAttribute("aria-label", "Filter by node type");

  filters.append(statusFilter, nodeTypeFilter);

  const hint = el("div", "run-history-hint muted");

  const list = el("div", "run-history-list");

  const wrap = el("div", "run-history-root");
  wrap.append(title, filters, hint, list);
  rootEl.replaceChildren(wrap);

  let workflowId = null;
  let status = "";
  let nodeType = "";

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
      const runId = run?.run_id ? String(run.run_id) : "";
      if (runId) {
        item.addEventListener("click", () => {
          onRunSelected?.(runId);
        });
      }
      const itemHeader = el("div", "run-history-item-header");

      const itemTitle = el("div", "run-history-item-title");
      itemTitle.textContent = formatRunItemTitle(run);

      if (runId && run?.has_checkpoint && onReplayRequested) {
        const replayButton = el("button", "run-history-action");
        replayButton.type = "button";
        replayButton.textContent = "Replay";
        replayButton.addEventListener("click", (event) => {
          event.preventDefault();
          event.stopPropagation();
          onReplayRequested(runId);
        });
        itemHeader.append(itemTitle, replayButton);
      } else {
        itemHeader.append(itemTitle);
      }

      const itemMeta = el("div", "run-history-item-meta");
      const metaParts = [];
      const meta = formatRunItemMeta(run);
      if (meta) metaParts.push(meta);
      if (run?.error) metaParts.push(String(run.error));
      itemMeta.textContent = metaParts.join(" • ");

      item.append(itemHeader, itemMeta);
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
      const result = await runHistoryApi.listRuns({
        workflowId,
        status: status || null,
        nodeType: nodeType || null,
        limit: 25,
      });
      renderRuns(result?.runs ?? []);
    } catch {
      renderHint(`Workflow: ${workflowId} (failed to load runs)`);
      renderRuns([]);
    }
  }

  function applyFilters() {
    status = statusFilter.value || "";
    nodeType = nodeTypeFilter.value.trim();
    void refresh();
  }

  statusFilter.addEventListener("change", applyFilters);
  nodeTypeFilter.addEventListener("change", applyFilters);

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
