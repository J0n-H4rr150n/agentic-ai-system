/**
 * Load a persisted run detail and (when available) its workflow graph.
 *
 * This stays DOM-free so it can be unit-tested.
 *
 * @param {{
 *  runId: string,
 *  runHistoryApi: { getRun: Function },
 *  workflowApi: { getWorkflow: Function },
 * }} params
 */
export async function loadPersistedRun({ runId, runHistoryApi, workflowApi }) {
  if (typeof runId !== "string" || !runId) {
    throw new Error("runId must be a non-empty string");
  }
  if (!runHistoryApi || typeof runHistoryApi.getRun !== "function") {
    throw new Error("runHistoryApi.getRun is required");
  }
  if (!workflowApi || typeof workflowApi.getWorkflow !== "function") {
    throw new Error("workflowApi.getWorkflow is required");
  }

  const detail = await runHistoryApi.getRun(runId);
  const workflowId = detail?.workflow_id ?? null;

  let graph = null;
  if (typeof workflowId === "string" && workflowId) {
    try {
      const wf = await workflowApi.getWorkflow(workflowId);
      graph = wf?.graph ?? null;
    } catch {
      graph = null;
    }
  }

  return {
    runId: detail?.run_id ?? runId,
    status: detail?.status ?? "completed",
    error: detail?.error ?? null,
    workflowId,
    graph,
    trace: Array.isArray(detail?.trace) ? detail.trace : [],
  };
}
