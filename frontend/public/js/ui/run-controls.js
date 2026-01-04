import { RUN_STATUSES } from "./status.js";
import { createSseStream } from "../sse/stream.js";

/**
 * @param {number} ms
 */
function defaultSleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTerminalStatus(status) {
  return status === RUN_STATUSES.COMPLETED || status === RUN_STATUSES.FAILED;
}

/**
 * @param {{
 *   runApi: { startRun: Function, getRun: Function, openRunStream?: Function },
 *   getGraph: Function,
 *   onStatus: Function,
 *   pollIntervalMs?: number,
 *   sleepImpl?: Function,
 *   useSse?: boolean,
 *   createSseStreamImpl?: typeof createSseStream,
 *   EventSourceImpl?: typeof EventSource,
 * }} params
 */
export function createRunController({
  runApi,
  getGraph,
  onStatus,
  pollIntervalMs = 400,
  sleepImpl = defaultSleep,
  useSse = true,
  createSseStreamImpl = createSseStream,
  EventSourceImpl = typeof EventSource === "undefined" ? null : EventSource,
}) {
  if (!runApi || typeof runApi.startRun !== "function" || typeof runApi.getRun !== "function") {
    throw new Error("runApi must provide startRun() and getRun()");
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
  if (typeof createSseStreamImpl !== "function") {
    throw new Error("createSseStreamImpl must be a function");
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

      let done = false;
      /** @type {null | { close: Function }} */
      let stream = null;

      if (useSse && typeof runApi.getRunStreamUrl === "function" && EventSourceImpl) {
        try {
          const url = runApi.getRunStreamUrl(runId);
          stream = createSseStreamImpl({
            url,
            EventSourceImpl,
            onEvent: (eventName, payload) => {
              if (eventName === "status") {
                const status = payload?.status;
                const error = payload?.error ?? null;
                if (status) {
                  onStatus(status, { runId, error });
                  if (isTerminalStatus(status)) {
                    done = true;
                    stream?.close();
                  }
                }
              }
            },
          }).connect();
        } catch {
          // Ignore SSE setup errors; fall back to polling.
        }
      }

      while (true) {
        if (done) {
          return;
        }
        await sleepImpl(pollIntervalMs);

        // If SSE is connected, prefer its real-time status events.
        if (stream) {
          continue;
        }

        const current = await runApi.getRun(runId);
        const status = current?.status;
        const error = current?.error ?? null;

        if (status && status !== RUN_STATUSES.RUNNING) {
          onStatus(status, { runId, error });
          stream?.close();
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
