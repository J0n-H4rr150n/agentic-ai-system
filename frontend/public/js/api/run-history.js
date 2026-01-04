import { createApiClient } from "./client.js";

/**
 * @param {{ client?: ReturnType<typeof createApiClient>, baseUrl?: string, fetchImpl?: typeof fetch }} [options]
 */
export function createRunHistoryApi(options = {}) {
  const client =
    options.client ?? createApiClient({ baseUrl: options.baseUrl ?? "/api", fetchImpl: options.fetchImpl });

  /**
   * @param {{ workflowId?: string | null, limit?: number, signal?: AbortSignal }} [params]
   */
  async function listRuns({ workflowId = null, limit = 100, signal } = {}) {
    if (workflowId !== null && (typeof workflowId !== "string" || !workflowId)) {
      throw new Error("workflowId must be a non-empty string when provided");
    }
    if (typeof limit !== "number" || !Number.isFinite(limit) || limit < 1) {
      throw new Error("limit must be a number >= 1");
    }

    const qs = new URLSearchParams();
    if (workflowId) {
      qs.set("workflow_id", workflowId);
    }
    qs.set("limit", String(Math.floor(limit)));

    const suffix = qs.toString();
    return client.requestJson(`/runs${suffix ? `?${suffix}` : ""}`, {
      method: "GET",
      signal,
    });
  }

  return {
    listRuns,
  };
}
