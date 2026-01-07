import test from "node:test";
import assert from "node:assert/strict";

import { createRunApi } from "../../public/js/api/run.js";

function makeFetch() {
  return async (url, options) => {
    // Simple route simulator.
    if (url === "/api/run" && options?.method === "POST") {
      const payload = JSON.parse(options?.body ?? "{}");
      if (payload?.workflow_id !== undefined && payload.workflow_id !== null && payload.workflow_id !== "w1") {
        throw new Error("unexpected workflow_id");
      }
      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return "{\"run_id\":\"r1\",\"status\":\"running\"}";
        },
      };
    }

    if (url === "/api/run/r1" && options?.method === "GET") {
      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return "{\"run_id\":\"r1\",\"status\":\"completed\"}";
        },
      };
    }

    if (url === "/api/run/r1/checkpoint" && options?.method === "GET") {
      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return "{\"run_id\":\"r1\",\"created_at\":\"2026-01-01T00:00:00Z\",\"state\":{},\"completed_node_ids\":[],\"ready_node_ids\":[],\"indegree\":{},\"handled_interrupts\":[]}";
        },
      };
    }

    if (url === "/api/run/r1/hitl/edit" && options?.method === "POST") {
      const payload = JSON.parse(options?.body ?? "{}");
      if (typeof payload?.state_patch !== "object") {
        throw new Error("missing state_patch");
      }
      return {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        async text() {
          return "{\"run_id\":\"r1\",\"status\":\"running\"}";
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

test("createRunApi.startRun POSTs graph and returns run_id", async () => {
  const api = createRunApi({ baseUrl: "/api", fetchImpl: makeFetch() });

  const graph = { version: 1, nodes: [], edges: [] };
  const result = await api.startRun({ graph });

  assert.deepEqual(result, { run_id: "r1", status: "running" });
});

test("createRunApi.startRun includes workflow_id when workflowId provided", async () => {
  const api = createRunApi({ baseUrl: "/api", fetchImpl: makeFetch() });

  const graph = { version: 1, nodes: [], edges: [] };
  const result = await api.startRun({ graph, workflowId: "w1" });

  assert.deepEqual(result, { run_id: "r1", status: "running" });
});

test("createRunApi.getRun GETs status", async () => {
  const api = createRunApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.getRun("r1");
  assert.deepEqual(result, { run_id: "r1", status: "completed" });
});

test("createRunApi.getCheckpoint GETs checkpoint", async () => {
  const api = createRunApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.getCheckpoint("r1");
  assert.equal(result.run_id, "r1");
  assert.ok(result.state);
});

test("createRunApi.hitlEdit POSTs state_patch", async () => {
  const api = createRunApi({ baseUrl: "/api", fetchImpl: makeFetch() });
  const result = await api.hitlEdit("r1", { statePatch: { approval_result: "approved" } });
  assert.deepEqual(result, { run_id: "r1", status: "running" });
});

test("createRunApi.openRunStream uses /api baseUrl", () => {
  class FakeEventSource {
    constructor(url) {
      this.url = url;
    }
  }

  const api = createRunApi({ baseUrl: "/api" });
  const es = api.openRunStream("r1", { EventSourceImpl: FakeEventSource });
  assert.equal(es.url, "/api/run/r1/stream");
});

test("createRunApi.getRunStreamUrl builds stream url", () => {
  const api = createRunApi({ baseUrl: "/api" });
  assert.equal(api.getRunStreamUrl("r1"), "/api/run/r1/stream");
});
