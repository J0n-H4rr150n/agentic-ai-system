import test from "node:test";
import assert from "node:assert/strict";

import { createRunHistoryApi } from "../../public/js/api/run-history.js";

function makeFetch() {
  return async (url, options) => {
    if (url.startsWith("/api/runs") && options?.method === "GET") {
      if (url === "/api/runs/r1") {
        return {
          ok: true,
          status: 200,
          headers: new Headers({ "content-type": "application/json" }),
          async text() {
            return JSON.stringify({
              run_id: "r1",
              workflow_id: "w1",
              status: "completed",
              started_at: "2026-01-04T00:00:00Z",
              completed_at: "2026-01-04T00:00:01Z",
              trace: [{ node_id: "a", status: "completed" }],
              error: null,
              checkpoint: null,
            });
          },
        };
      }

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
                has_checkpoint: true,
              },
            ],
          });
        },
      };
    }

    if (url === "/api/runs/r1/replay" && options?.method === "POST") {
      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return JSON.stringify({ run_id: "r2", status: "running" });
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

test("createRunHistoryApi.getRun GETs /runs/{id}", async () => {
  const api = createRunHistoryApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.getRun("r1");

  assert.equal(result.run_id, "r1");
  assert.equal(result.workflow_id, "w1");
  assert.ok(Array.isArray(result.trace));
});

test("createRunHistoryApi.replayRun POSTs /runs/{id}/replay", async () => {
  const api = createRunHistoryApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.replayRun("r1");

  assert.equal(result.run_id, "r2");
  assert.equal(result.status, "running");
});
