import { RUN_STATUSES } from "./status.js";
import { createSseStream } from "../sse/stream.js";
import { showApprovalModal } from "./approval-modal.js";

/**
 * @param {number} ms
 */
function defaultSleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTerminalStatus(status) {
  return status === RUN_STATUSES.COMPLETED || status === RUN_STATUSES.CANCELLED || status === RUN_STATUSES.FAILED;
}

function isPaused(status) {
  return status === "paused";
}

/**
 * @param {{
 *   runApi: { startRun: Function, getRun: Function, openRunStream?: Function },
 *   getGraph: Function,
 *   getWorkflowId?: Function,
 *   onRunStart?: Function,
 *   onStatus: Function,
 *   onStep?: Function,
 *   pollIntervalMs?: number,
 *   sleepImpl?: Function,
 *   useSse?: boolean,
 *   createSseStreamImpl?: typeof createSseStream,
 *   EventSourceImpl?: typeof EventSource,
 *   showApprovalModalImpl?: typeof showApprovalModal,
 * }} params
 */
export function createRunController({
  runApi,
  getGraph,
  getWorkflowId,
  onRunStart,
  onStatus,
  onStep,
  pollIntervalMs = 400,
  sleepImpl = defaultSleep,
  useSse = true,
  createSseStreamImpl = createSseStream,
  EventSourceImpl = typeof EventSource === "undefined" ? null : EventSource,
  showApprovalModalImpl = showApprovalModal,
}) {
  if (!runApi || typeof runApi.startRun !== "function" || typeof runApi.getRun !== "function") {
    throw new Error("runApi must provide startRun() and getRun()");
  }
  if (typeof getGraph !== "function") {
    throw new Error("getGraph must be a function");
  }
  if (getWorkflowId !== undefined && typeof getWorkflowId !== "function") {
    throw new Error("getWorkflowId must be a function if provided");
  }
  if (typeof onStatus !== "function") {
    throw new Error("onStatus must be a function");
  }
  if (onRunStart !== undefined && typeof onRunStart !== "function") {
    throw new Error("onRunStart must be a function if provided");
  }
  if (onStep !== undefined && typeof onStep !== "function") {
    throw new Error("onStep must be a function if provided");
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
      const workflowId = getWorkflowId?.() ?? null;
      onRunStart?.(graph);
      onStatus(RUN_STATUSES.RUNNING, { runId: null, error: null });

      const created = await runApi.startRun({ graph, workflowId });
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
              if (eventName === "step") {
                onStep?.(payload);
              }
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

      async function handlePotentialHumanApprovalPause(current) {
        const status = current?.status;
        if (!isPaused(status)) {
          return false;
        }

        // Only handle interrupt pauses that provide a pending_interrupt.
        const pauseReason = current?.pause_reason ?? null;
        const pending = current?.pending_interrupt ?? null;
        if (pauseReason !== "interrupt" || !pending?.node_id) {
          return false;
        }

        // Lookup node config from the graph we started.
        const nodeId = pending.node_id;
        const node = (graph?.nodes ?? []).find((n) => n?.id === nodeId) ?? null;
        if (node?.type !== "human_approval") {
          return false;
        }

        // Pull checkpoint state for context.
        const checkpoint = typeof runApi.getCheckpoint === "function" ? await runApi.getCheckpoint(runId) : null;
        const state = checkpoint?.state && typeof checkpoint.state === "object" ? checkpoint.state : {};

        const title = node?.config?.title ?? "Human Approval Required";
        const message = node?.config?.message ?? "";
        const timeoutSeconds = node?.config?.timeout_seconds ?? null;

        let keys = [];
        try {
          const raw = node?.config?.show_state_keys;
          keys = typeof raw === "string" && raw.trim() ? JSON.parse(raw) : [];
        } catch {
          keys = [];
        }

        const contextEntries = Array.isArray(keys)
          ? keys
              .filter((k) => typeof k === "string" && k)
              .map((k) => ({
                key: k,
                valueText: (() => {
                  const v = state[k];
                  if (v === undefined) return "";
                  try {
                    return typeof v === "string" ? v : JSON.stringify(v);
                  } catch {
                    return String(v);
                  }
                })(),
              }))
          : [];

        const approved = await showApprovalModalImpl({
          title,
          message,
          contextEntries,
          timeoutSeconds: typeof timeoutSeconds === "number" ? timeoutSeconds : null,
        });

        if (typeof runApi.hitlEdit !== "function") {
          throw new Error("runApi must provide hitlEdit() to handle approvals");
        }

        await runApi.hitlEdit(runId, {
          statePatch: {
            approval_result: approved ? "approved" : "rejected",
          },
        });

        // After HITL edit, the backend resumes; continue monitoring.
        return true;
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

          // If we paused due to a Human Approval node, handle it and keep going.
          const resumed = await handlePotentialHumanApprovalPause(current);
          if (resumed) {
            continue;
          }

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
