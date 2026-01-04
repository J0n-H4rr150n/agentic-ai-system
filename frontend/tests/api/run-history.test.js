import test from "node:test";
import assert from "node:assert/strict";

import { createRunHistoryApi } from "../../public/js/api/run-history.js";

function makeFetch() {
  return async (url, options) => {
    if (url.startsWith("/api/runs") && options?.method === "GET") {
      const u = new URL(url, "http://example.local");
      const workflowId = u.searchParams.get("workflow_id");

      if (workflowId && workflowId !== "w1") {
        return {
          ok: true,
          status: 200,
          headers: new Headers({ "content-type": "application/json" }),
          async text() {
            return JSON.stringify({ runs: [] });
          },
        };
      }

      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return JSON.stringify({
            runs: [
              {
                run_id: "r1",
                workflow_id: workflowId,
                status: "completed",
                started_at: "2026-01-04T00:00:00Z",
                completed_at: "2026-01-04T00:00:01Z",
                error: null,
              },
            ],
          });
        },
      };
    }

    return {
      ok: false,
      status: 500,
      headers: new Headers({ "content-type": "text/plain" }),
      async text() {
        return "unexpected";
      },
    };
  };
}

test("createRunHistoryApi.listRuns GETs /runs", async () => {
  const api = createRunHistoryApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.listRuns();

  assert.ok(Array.isArray(result.runs));
  assert.equal(result.runs[0].run_id, "r1");
});

test("createRunHistoryApi.listRuns includes workflow_id when workflowId provided", async () => {
  const api = createRunHistoryApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.listRuns({ workflowId: "w1" });

  assert.equal(result.runs[0].workflow_id, "w1");
});
