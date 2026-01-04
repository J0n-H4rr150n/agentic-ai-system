import { createApiClient } from "./client.js";

/**
 * @param {{ client?: ReturnType<typeof createApiClient>, baseUrl?: string, fetchImpl?: typeof fetch }} [options]
 */
export function createRunApi(options = {}) {
  const client = options.client ?? createApiClient({ baseUrl: options.baseUrl ?? "/api", fetchImpl: options.fetchImpl });

  async function startRun({ graph, mode = "run", signal } = {}) {
    if (!graph || typeof graph !== "object") {
      throw new Error("graph must be an object");
    }

    return client.requestJson("/run", {
      method: "POST",
      json: { graph, mode },
      signal,
    });
  }

  async function getRun(runId, { signal } = {}) {
    if (typeof runId !== "string" || !runId) {
      throw new Error("runId must be a non-empty string");
    }

    return client.requestJson(`/run/${encodeURIComponent(runId)}`, {
      method: "GET",
      signal,
    });
  }

  function openRunStream(runId, { EventSourceImpl = EventSource } = {}) {
    if (typeof runId !== "string" || !runId) {
      throw new Error("runId must be a non-empty string");
    }
    if (typeof EventSourceImpl !== "function") {
      throw new Error("EventSourceImpl must be a constructor");
    }

    const baseUrl = options.baseUrl ?? "/api";
    const base = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
    const url = `${base}/run/${encodeURIComponent(runId)}/stream`;

    return new EventSourceImpl(url);
  }

  return {
    startRun,
    getRun,
    openRunStream,
  };
}
