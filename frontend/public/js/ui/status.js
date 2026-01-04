export const RUN_STATUSES = /** @type {const} */ ({
  IDLE: "idle",
  RUNNING: "running",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
  FAILED: "failed",
});

/**
 * @param {{ status: string, runId?: string | null, error?: string | null }} params
 */
export function formatRunStatusText({ status, runId = null, error = null }) {
  if (status === RUN_STATUSES.IDLE) {
    return "Status: idle";
  }

  if (status === RUN_STATUSES.RUNNING) {
    return runId ? `Status: running (${runId})` : "Status: running";
  }

  if (status === RUN_STATUSES.COMPLETED) {
    return runId ? `Status: completed (${runId})` : "Status: completed";
  }

  if (status === RUN_STATUSES.CANCELLED) {
    return runId ? `Status: cancelled (${runId})` : "Status: cancelled";
  }

  if (status === RUN_STATUSES.FAILED) {
    if (runId && error) {
      return `Status: failed (${runId}) - ${error}`;
    }
    if (error) {
      return `Status: failed - ${error}`;
    }
    return runId ? `Status: failed (${runId})` : "Status: failed";
  }

  return "Status: idle";
}

/**
 * @param {{ element: HTMLElement }} params
 */
export function createRunStatusIndicator({ element }) {
  if (!element) {
    throw new Error("element is required");
  }

  let current = { status: RUN_STATUSES.IDLE, runId: null, error: null };

  function setStatus(status, { runId = null, error = null } = {}) {
    current = { status, runId, error };
    element.textContent = formatRunStatusText(current);
  }

  // Initialize.
  setStatus(RUN_STATUSES.IDLE);

  return {
    setStatus,
    getCurrent() {
      return { ...current };
    },
  };
}
