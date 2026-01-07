import test from "node:test";
import assert from "node:assert/strict";

import { createRunController } from "../../public/js/ui/run-controls.js";
import { RUN_STATUSES, formatRunStatusText } from "../../public/js/ui/status.js";

test("formatRunStatusText renders idle/running/completed/failed", () => {
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.IDLE }), "Status: idle");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.RUNNING }), "Status: running");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.RUNNING, runId: "r1" }), "Status: running (r1)");
  assert.equal(formatRunStatusText({ status: RUN_STATUSES.PAUSED, runId: "r1" }), "Status: paused (r1)");
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


test("createRunController handles human_approval interrupt pause via hitlEdit", async () => {
  const statuses = [];

  const graph = {
    version: 1,
    nodes: [
      { id: "h1", type: "human_approval", config: { title: "t", message: "m", show_state_keys: "[]", timeout_seconds: 1 } },
    ],
    edges: [],
  };

  let getCalls = 0;
  let hitlCalls = 0;

  const runApi = {
    async startRun() {
      return { run_id: "r1", status: "running" };
    },
    async getRun() {
      getCalls += 1;
      if (getCalls === 1) {
        return { status: "paused", pause_reason: "interrupt", pending_interrupt: { node_id: "h1", phase: "before" } };
      }
      return { status: "completed" };
    },
    async getCheckpoint() {
      return { state: {} };
    },
    async hitlEdit(runId, { statePatch }) {
      hitlCalls += 1;
      assert.equal(runId, "r1");
      assert.equal(statePatch.approval_result, "rejected");
      return { run_id: "r1", status: "running" };
    },
  };

  // Mock showApprovalModal to auto-reject (returns false).
  const { showApprovalModal } = await import("../../public/js/ui/approval-modal.js");
  const originalFn = showApprovalModal;
  const mockImpl = async () => false;

  const controller = createRunController({
    runApi,
    getGraph: () => graph,
    onStatus: (status, details) => statuses.push({ status, details }),
    pollIntervalMs: 1,
    sleepImpl: async () => {},
    useSse: false,
    // Inject mock approval modal.
    showApprovalModalImpl: mockImpl,
  });

  await controller.runOnce();
  assert.equal(hitlCalls, 1);
  assert.equal(statuses.at(-1).status, "completed");
});
