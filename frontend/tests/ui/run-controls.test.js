import test from "node:test";
import assert from "node:assert/strict";

import { createRunController } from "../../public/js/ui/run-controls.js";
import { RUN_STATUSES, formatRunStatusText } from "../../public/js/ui/status.js";

test("formatRunStatusText renders idle/running/completed/failed", () => {
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.IDLE }), "Status: idle");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.RUNNING }), "Status: running");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.RUNNING, runId: "r1" }), "Status: running (r1)");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.COMPLETED, runId: "r1" }), "Status: completed (r1)");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.CANCELLED, runId: "r1" }), "Status: cancelled (r1)");
  assert.equal(
    formatRunStatusText({ status: RUN_STATUSES.FAILED, runId: "r1", error: "boom" }),
    "Status: failed (r1) - boom",
  );
});

test("createRunController runOnce starts run and polls until not running", async () => {
  const statuses = [];

  let seenWorkflowId = null;

  const runApi = {
    async startRun({ workflowId }) {
      seenWorkflowId = workflowId ?? null;
      return { run_id: "r1", status: "running" };
    },
    calls: 0,
    async getRun(runId) {
      assert.equal(runId, "r1");
      this.calls += 1;
      if (this.calls < 2) {
        return { run_id: "r1", status: "running" };
      }
      return { run_id: "r1", status: "completed" };
    },
  };

  const controller = createRunController({
    runApi,
    getGraph: () => ({ version: 1, nodes: [], edges: [] }),
    getWorkflowId: () => "w1",
    onStatus: (status, details) => statuses.push({ status, details }),
    pollIntervalMs: 1,
    sleepImpl: async () => {},
  });

  await controller.runOnce();

  assert.equal(seenWorkflowId, "w1");

  assert.equal(statuses[0].status, "running");
  assert.equal(statuses[1].status, "running");
  assert.equal(statuses[1].details.runId, "r1");
  assert.equal(statuses.at(-1).status, "completed");
});

test("createRunController runOnce reports failed on exceptions", async () => {
  const statuses = [];

  const controller = createRunController({
    runApi: {
      async startRun() {
        throw new Error("nope");
      },
      async getRun() {
        return null;
      },
    },
    getGraph: () => ({ version: 1, nodes: [], edges: [] }),
    onStatus: (status, details) => statuses.push({ status, details }),
    sleepImpl: async () => {},
  });

  await controller.runOnce();
  assert.equal(statuses.at(-1).status, "failed");
  assert.match(statuses.at(-1).details.error, /nope/);
});
