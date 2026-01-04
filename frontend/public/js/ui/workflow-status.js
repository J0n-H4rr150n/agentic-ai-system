export const WORKFLOW_SAVE_STATUSES = /** @type {const} */ ({
  IDLE: "idle",
  SAVING: "saving",
  SAVED: "saved",
  FAILED: "failed",
});

/**
 * @param {{ status: string, workflowId?: string | null, error?: string | null }} params
 */
export function formatWorkflowStatusText({ status, workflowId = null, error = null }) {
  if (status === WORKFLOW_SAVE_STATUSES.IDLE) {
    return "Workflow: idle";
  }

  if (status === WORKFLOW_SAVE_STATUSES.SAVING) {
    return "Workflow: saving...";
  }

  if (status === WORKFLOW_SAVE_STATUSES.SAVED) {
    return workflowId ? `Workflow: saved (${workflowId})` : "Workflow: saved";
  }

  if (status === WORKFLOW_SAVE_STATUSES.FAILED) {
    if (workflowId && error) {
      return `Workflow: failed (${workflowId}) - ${error}`;
    }
    if (error) {
      return `Workflow: failed - ${error}`;
    }
    return workflowId ? `Workflow: failed (${workflowId})` : "Workflow: failed";
  }

  return "Workflow: idle";
}

/**
 * @param {{ element: HTMLElement }} params
 */
export function createWorkflowStatusIndicator({ element }) {
  if (!element) {
    throw new Error("element is required");
  }

  let current = { status: WORKFLOW_SAVE_STATUSES.IDLE, workflowId: null, error: null };

  function setStatus(status, { workflowId = null, error = null } = {}) {
    current = { status, workflowId, error };
    element.textContent = formatWorkflowStatusText(current);
  }

  setStatus(WORKFLOW_SAVE_STATUSES.IDLE);

  return {
    setStatus,
    getCurrent() {
      return { ...current };
    },
  };
}
