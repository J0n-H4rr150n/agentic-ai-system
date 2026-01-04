import { RUN_STATUSES } from "./status.js";

/**
 * @param {number} ms
 */
function defaultSleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * @param {{ runApi: { startRun: Function, getRun: Function }, getGraph: Function, onStatus: Function, pollIntervalMs?: number, sleepImpl?: Function }} params
 */
export function createRunController({ runApi, getGraph, onStatus, pollIntervalMs = 400, sleepImpl = defaultSleep }) {
  if (!runApi || typeof runApi.startRun !== "function" || typeof runApi.getRun !== "function") {
    throw new Error("runApi must provide startRun() and getRun()")
  }
  if (typeof getGraph !== "function") {
    throw new Error("getGraph must be a function");
  }
  if (typeof onStatus !== "function") {
    throw new Error("onStatus must be a function");
  }
  if (typeof sleepImpl !== "function") {
    throw new Error("sleepImpl must be a function");
  }

  let inFlight = false;

  async function runOnce() {
    if (inFlight) {
      return;
    }
    inFlight = true;

    try {
      const graph = getGraph();
      onStatus(RUN_STATUSES.RUNNING, { runId: null, error: null });

      const created = await runApi.startRun({ graph });
      const runId = created?.run_id;

      // Default to running unless backend says otherwise.
      const initialStatus = created?.status ?? RUN_STATUSES.RUNNING;
      onStatus(initialStatus, { runId, error: null });

      if (initialStatus !== RUN_STATUSES.RUNNING || !runId) {
        return;
      }

      while (true) {
        await sleepImpl(pollIntervalMs);
        const current = await runApi.getRun(runId);
        const status = current?.status;
        const error = current?.error ?? null;

        if (status && status !== RUN_STATUSES.RUNNING) {
          onStatus(status, { runId, error });
          return;
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      onStatus(RUN_STATUSES.FAILED, { runId: null, error: message });
    } finally {
      inFlight = false;
    }
  }

  return {
    runOnce,
  };
}
