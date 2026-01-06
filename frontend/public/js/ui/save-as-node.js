import { WORKFLOW_SAVE_STATUSES } from "./workflow-status.js";

/**
 * @param {{
 *  workflowApi: { createWorkflow: Function },
 *  getGraph: Function,
 *  onStatus: Function,
 * }} params
 */
export function createSaveAsNodeController({ workflowApi, getGraph, onStatus }) {
  if (!workflowApi || typeof workflowApi.createWorkflow !== "function") {
    throw new Error("workflowApi must provide createWorkflow()");
  }
  if (typeof getGraph !== "function") {
    throw new Error("getGraph must be a function");
  }
  if (typeof onStatus !== "function") {
    throw new Error("onStatus must be a function");
  }

  let inFlight = false;

  async function save() {
    if (inFlight) {
      return;
    }

    // Prompt for workflow name
    const name = prompt("Enter a name for this workflow:", "My Workflow");
    if (!name || !name.trim()) {
      // User cancelled or entered empty name
      return;
    }

    inFlight = true;

    try {
      const graph = getGraph();
      onStatus(WORKFLOW_SAVE_STATUSES.SAVING, { workflowId: null, error: null });

      const created = await workflowApi.createWorkflow({
        graph,
        name: name.trim()
      });
      const workflowId = created?.workflow_id ?? null;

      onStatus(WORKFLOW_SAVE_STATUSES.SAVED, { workflowId, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      onStatus(WORKFLOW_SAVE_STATUSES.FAILED, { workflowId: null, error: message });
    } finally {
      inFlight = false;
    }
  }

  return {
    save,
  };
}
