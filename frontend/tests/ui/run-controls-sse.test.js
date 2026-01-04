import test from "node:test";
import assert from "node:assert/strict";

import { createRunController } from "../../public/js/ui/run-controls.js";

class FakeEventSource {
  constructor(url) {
    this.url = url;
    this.onopen = null;
    this.onerror = null;
    this._listeners = new Map();
  }

  addEventListener(name, handler) {
    const list = this._listeners.get(name) ?? [];
    list.push(handler);
    this._listeners.set(name, list);
  }

  emit(name, payload) {
    const handlers = this._listeners.get(name) ?? [];
    for (const h of handlers) {
      h({ data: JSON.stringify(payload) });
    }
  }

  close() {}
}

test("run controller uses SSE status events to finish early", async () => {
  const statuses = [];

  let es = null;

  const runApi = {
    async startRun() {
      return { run_id: "r1", status: "running" };
    },
    async getRun() {
      throw new Error("polling should not be needed");
    },
    getRunStreamUrl(runId) {
      return `/api/run/${runId}/stream`;
    },
  };

  const controller = createRunController({
    runApi,
    getGraph: () => ({ version: 1, nodes: [], edges: [] }),
    onStatus: (status, details) => statuses.push({ status, details }),
    pollIntervalMs: 1,
    sleepImpl: async () => {
      await Promise.resolve();
    },
    useSse: true,
    EventSourceImpl: class extends FakeEventSource {
      constructor(url) {
        super(url);
        es = this;
      }
    },
  });

  const runPromise = controller.runOnce();

  // Let startRun() complete and SSE connect.
  await Promise.resolve();
  await Promise.resolve();

  // Emit terminal status.
  es.emit("status", { run_id: "r1", status: "completed" });

  await runPromise;
  assert.equal(statuses.at(-1).status, "completed");
});
