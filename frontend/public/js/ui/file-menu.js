/**
 * Minimal "File" menu controller.
 *
 * This module intentionally avoids hard-coding app-specific logic; callers provide
 * callbacks for exporting JSON and importing a workflow graph.
 */

function requireElement(el, message) {
  if (!el) {
    throw new Error(message);
  }
  return el;
}

function normalizeWorkflowsResponse(result) {
  const workflows = Array.isArray(result?.workflows) ? result.workflows : [];
  return workflows
    .map((w) => ({
      workflowId: typeof w?.workflow_id === "string" ? w.workflow_id : "",
      name: typeof w?.name === "string" && w.name ? w.name : null,
      latestVersion: Number.isFinite(w?.latest_version) ? w.latest_version : null,
    }))
    .filter((w) => Boolean(w.workflowId));
}

function renderWorkflowOptions({ document, selectEl, workflows }) {
  selectEl.replaceChildren();

  if (!workflows.length) {
    const opt = document.createElement("option");
    opt.value = "";
    const displayName = wf.name || wf.workflowId;
    const version = typeof wf.latestVersion === "number" ? ` (v${wf.latestVersion})` : "";
    opt.textContent = "No workflows (use Save)";
    selectEl.appendChild(opt);
    return;
  }

  for (const wf of workflows) {
    const opt = document.createElement("option");
    opt.value = wf.workflowId;
    const displayName = wf.name || wf.workflowId;
    const version = typeof wf.latestVersion === "number" ? ` (v${wf.latestVersion})` : "";
    opt.textContent =
      `${displayName}${version}`;
    selectEl.appendChild(opt);
  }

  // Default to the first workflow.
  selectEl.value = workflows[0].workflowId;
}

/**
 * @param {{
 *   buttonEl: HTMLElement,
 *   menuEl: HTMLElement,
 *   workflowSelectEl: HTMLSelectElement,
 *   loadWorkflowButtonEl: HTMLButtonElement,
 *   exportJsonButtonEl: HTMLButtonElement,
 *   importJsonButtonEl: HTMLButtonElement,
 *   importJsonInputEl: HTMLInputElement,
 *   workflowApi: { listWorkflows: Function, getWorkflow: Function },
 *   onImportGraph: (graph: any) => void,
 *   onWorkflowLoaded: (workflowId: string) => void,
 *   onExportJson: () => void,
 *   onResetUi?: () => void,
 *   document?: Document,
 * }} params
 */
export function createFileMenuController(params) {
  const document = params.document ?? globalThis.document;

  const buttonEl = requireElement(params.buttonEl, "buttonEl is required");
  const menuEl = requireElement(params.menuEl, "menuEl is required");
  const workflowSelectEl = requireElement(params.workflowSelectEl, "workflowSelectEl is required");
  const loadWorkflowButtonEl = requireElement(params.loadWorkflowButtonEl, "loadWorkflowButtonEl is required");
  const exportJsonButtonEl = requireElement(params.exportJsonButtonEl, "exportJsonButtonEl is required");
  const importJsonButtonEl = requireElement(params.importJsonButtonEl, "importJsonButtonEl is required");
  const importJsonInputEl = requireElement(params.importJsonInputEl, "importJsonInputEl is required");

  const workflowApi = requireElement(params.workflowApi, "workflowApi is required");
  const onImportGraph = requireElement(params.onImportGraph, "onImportGraph is required");
  const onWorkflowLoaded = requireElement(params.onWorkflowLoaded, "onWorkflowLoaded is required");
  const onExportJson = requireElement(params.onExportJson, "onExportJson is required");
  const onResetUi = params.onResetUi ?? null;

  let isOpen = false;
  let isLoadingList = false;

  function setOpen(nextOpen) {
    isOpen = Boolean(nextOpen);
    menuEl.classList.toggle("file-menu--open", isOpen);
    buttonEl.setAttribute("aria-expanded", isOpen ? "true" : "false");
    menuEl.setAttribute("aria-hidden", isOpen ? "false" : "true");

    if (!isOpen) {
      return;
    }

    // Fire-and-forget refresh; callers can also call refreshWorkflows() in tests.
    refreshWorkflows().catch(() => {
      // Ignore in MVP.
    });
  }

  async function refreshWorkflows() {
    if (isLoadingList) {
      return;
    }

    isLoadingList = true;
    workflowSelectEl.disabled = true;
    loadWorkflowButtonEl.disabled = true;

    try {
      const result = await workflowApi.listWorkflows();
      const workflows = normalizeWorkflowsResponse(result);
      renderWorkflowOptions({ document, selectEl: workflowSelectEl, workflows });

      workflowSelectEl.disabled = workflows.length === 0;
      loadWorkflowButtonEl.disabled = workflows.length === 0;
    } catch {
      workflowSelectEl.replaceChildren();
      const opt = document.createElement("option");
      opt.value = "";
      const displayName = wf.name || wf.workflowId;
      const version = typeof wf.latestVersion === "number" ? ` (v${wf.latestVersion})` : "";
      opt.textContent = "Failed to load";
      workflowSelectEl.appendChild(opt);
      workflowSelectEl.disabled = true;
      loadWorkflowButtonEl.disabled = true;
    } finally {
      isLoadingList = false;
    }
  }

  async function loadSelectedWorkflow() {
    const workflowId = workflowSelectEl.value;
    if (typeof workflowId !== "string" || !workflowId) {
      return;
    }

    loadWorkflowButtonEl.disabled = true;

    try {
      const wf = await workflowApi.getWorkflow(workflowId);
      const graph = wf?.graph ?? null;
      if (!graph || typeof graph !== "object") {
        return;
      }

      if (typeof onResetUi === "function") {
        onResetUi();
      }

      onImportGraph(graph);
      onWorkflowLoaded(workflowId);
      setOpen(false);
    } catch {
      // Ignore in MVP.
    } finally {
      loadWorkflowButtonEl.disabled = false;
    }
  }

  buttonEl.addEventListener("click", () => {
    setOpen(!isOpen);
  });

  exportJsonButtonEl.addEventListener("click", () => {
    onExportJson();
    setOpen(false);
  });

  loadWorkflowButtonEl.addEventListener("click", async () => {
    await loadSelectedWorkflow();
  });

  // Import JSON button triggers file picker
  importJsonButtonEl.addEventListener("click", () => {
    importJsonInputEl.click();
  });

  // Handle file selection
  importJsonInputEl.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const json = JSON.parse(text);

      // Check if JSON has a "graph" wrapper or is direct graph
      const graph = json.graph ?? json;

      if (!graph || typeof graph !== "object") {
        alert("Invalid workflow JSON: missing graph data");
        return;
      }

      if (typeof onResetUi === "function") {
        onResetUi();
      }

      onImportGraph(graph);
      setOpen(false);

      // Clear the input so the same file can be selected again
      importJsonInputEl.value = "";
    } catch (error) {
      alert(`Failed to import JSON: ${error.message}`);
      importJsonInputEl.value = "";
    }
  });

  // Initialize.
  buttonEl.setAttribute("aria-expanded", "false");
  menuEl.setAttribute("aria-hidden", "true");
  menuEl.classList.remove("file-menu--open");

  return {
    open: () => setOpen(true),
    close: () => setOpen(false),
    toggle: () => setOpen(!isOpen),
    isOpen: () => isOpen,
    refreshWorkflows,
    loadSelectedWorkflow,
  };
}
