import test from "node:test";
import assert from "node:assert/strict";

import { createWorkflowApi } from "../../public/js/api/workflow.js";

function createFakeClient() {
  /** @type {Array<{ path: string, options: any }>} */
  const calls = [];
  return {
    calls,
    requestJson: async (path, options) => {
      calls.push({ path, options });
      return { ok: true };
    },
  };
}

test("createWorkflowApi.createWorkflow POSTs /workflow", async () => {
  const fake = createFakeClient();
  const api = createWorkflowApi({ client: fake });

  await api.createWorkflow({ graph: { version: 1, nodes: [], edges: [] } });

  assert.equal(fake.calls.length, 1);
  assert.equal(fake.calls[0].path, "/workflow");
  assert.equal(fake.calls[0].options.method, "POST");
  assert.deepEqual(fake.calls[0].options.json, { graph: { version: 1, nodes: [], edges: [] } });
});

test("createWorkflowApi.getWorkflow GETs /workflow/{id}", async () => {
  const fake = createFakeClient();
  const api = createWorkflowApi({ client: fake });

  await api.getWorkflow("abc");

  assert.equal(fake.calls.length, 1);
  assert.equal(fake.calls[0].path, "/workflow/abc");
  assert.equal(fake.calls[0].options.method, "GET");
});

test("createWorkflowApi.getWorkflow validates workflowId", async () => {
  const api = createWorkflowApi({ client: createFakeClient() });
  await assert.rejects(() => api.getWorkflow(""), /workflowId must be a non-empty string/);
});
