import { createApiClient } from "./client.js";

/**
 * @param {{ client?: ReturnType<typeof createApiClient>, baseUrl?: string, fetchImpl?: typeof fetch }} [options]
 */
export function createWorkflowApi(options = {}) {
  const client =
    options.client ?? createApiClient({ baseUrl: options.baseUrl ?? "/api", fetchImpl: options.fetchImpl });

  async function createWorkflow({ graph, signal } = {}) {
    if (!graph || typeof graph !== "object") {
      throw new Error("graph must be an object");
    }

    return client.requestJson("/workflow", {
      method: "POST",
      json: { graph },
      signal,
    });
  }

  async function getWorkflow(workflowId, { signal } = {}) {
    if (typeof workflowId !== "string" || !workflowId) {
      throw new Error("workflowId must be a non-empty string");
    }

    return client.requestJson(`/workflow/${encodeURIComponent(workflowId)}`, {
      method: "GET",
      signal,
    });
  }


  async function listWorkflows({ signal } = {}) {
    return client.requestJson("/workflow", {
      method: "GET",
      signal,
    });
  }
  return {
    createWorkflow,
    getWorkflow,
    listWorkflows,
  };
}
