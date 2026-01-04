import test from "node:test";
import assert from "node:assert/strict";

import { loadPersistedRun } from "../../public/js/ui/run-history-loader.js";

function makeRunHistoryApi(detail) {
  return {
    async getRun(runId) {
      return { ...detail, run_id: runId };
    },
  };
}

function makeWorkflowApi({ graphById, throws } = {}) {
  return {
    async getWorkflow(workflowId) {
      if (throws) {
        throw new Error("workflow fetch failed");
      }
      const graph = graphById?.[workflowId] ?? null;
      return graph ? { graph } : null;
    },
  };
}

test("loadPersistedRun returns trace and no graph when workflow_id missing", async () => {
  const runHistoryApi = makeRunHistoryApi({
    workflow_id: null,
    status: "completed",
    error: null,
    trace: [{ node_id: "n1", status: "completed" }],
  });
  const workflowApi = makeWorkflowApi({
    graphById: { w1: { nodes: [] } },
  });

  const result = await loadPersistedRun({
    runId: "r1",
    runHistoryApi,
    workflowApi,
  });

  assert.equal(result.runId, "r1");
  assert.equal(result.workflowId, null);
  assert.equal(result.status, "completed");
  assert.deepEqual(result.trace, [{ node_id: "n1", status: "completed" }]);
  assert.equal(result.graph, null);
});

test("loadPersistedRun fetches workflow graph when workflow_id present", async () => {
  const runHistoryApi = makeRunHistoryApi({
    workflow_id: "w1",
    status: "completed",
    error: null,
    trace: [{ node_id: "n1", status: "completed" }],
  });
  const workflowApi = makeWorkflowApi({
    graphById: { w1: { nodes: [{ id: "n1", type: "noop" }] } },
  });

  const result = await loadPersistedRun({
    runId: "r1",
    runHistoryApi,
    workflowApi,
  });

  assert.equal(result.workflowId, "w1");
  assert.deepEqual(result.graph, { nodes: [{ id: "n1", type: "noop" }] });
});

test("loadPersistedRun tolerates workflow fetch failure", async () => {
  const runHistoryApi = makeRunHistoryApi({
    workflow_id: "w1",
    status: "completed",
    error: null,
    trace: [{ node_id: "n1", status: "completed" }],
  });
  const workflowApi = makeWorkflowApi({ throws: true });

  const result = await loadPersistedRun({
    runId: "r1",
    runHistoryApi,
    workflowApi,
  });

  assert.equal(result.workflowId, "w1");
  assert.equal(result.graph, null);
  assert.deepEqual(result.trace, [{ node_id: "n1", status: "completed" }]);
});
