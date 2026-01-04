import test from "node:test";
import assert from "node:assert/strict";

import { createSaveAsNodeController } from "../../public/js/ui/save-as-node.js";
import { WORKFLOW_SAVE_STATUSES } from "../../public/js/ui/workflow-status.js";

test("createSaveAsNodeController save posts graph and reports saved", async () => {
  const statuses = [];

  /** @type {any} */
  let capturedGraph = null;

  const workflowApi = {
    async createWorkflow({ graph }) {
      capturedGraph = graph;
      return { workflow_id: "w1" };
    },
  };

  const controller = createSaveAsNodeController({
    workflowApi,
    getGraph: () => ({ version: 1, nodes: [], edges: [] }),
    onStatus: (status, details) => statuses.push({ status, details }),
  });

  await controller.save();

  assert.deepEqual(capturedGraph, { version: 1, nodes: [], edges: [] });
  assert.equal(statuses[0].status, WORKFLOW_SAVE_STATUSES.SAVING);
  assert.equal(statuses.at(-1).status, WORKFLOW_SAVE_STATUSES.SAVED);
  assert.equal(statuses.at(-1).details.workflowId, "w1");
});

test("createSaveAsNodeController save reports failed on exceptions", async () => {
  const statuses = [];

  const controller = createSaveAsNodeController({
    workflowApi: {
      async createWorkflow() {
        throw new Error("boom");
      },
    },
    getGraph: () => ({ version: 1, nodes: [], edges: [] }),
    onStatus: (status, details) => statuses.push({ status, details }),
  });

  await controller.save();

  assert.equal(statuses[0].status, WORKFLOW_SAVE_STATUSES.SAVING);
  assert.equal(statuses.at(-1).status, WORKFLOW_SAVE_STATUSES.FAILED);
  assert.match(statuses.at(-1).details.error, /boom/);
});
