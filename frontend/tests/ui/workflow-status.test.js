import test from "node:test";
import assert from "node:assert/strict";

import { WORKFLOW_SAVE_STATUSES, formatWorkflowStatusText } from "../../public/js/ui/workflow-status.js";

test("formatWorkflowStatusText renders idle/saving/saved/failed", () => {
  assert.equal(formatWorkflowStatusText({ status: WORKFLOW_SAVE_STATUSES.IDLE }), "Workflow: idle");
  assert.equal(formatWorkflowStatusText({ status: WORKFLOW_SAVE_STATUSES.SAVING }), "Workflow: saving...");
  assert.equal(
    formatWorkflowStatusText({ status: WORKFLOW_SAVE_STATUSES.SAVED, workflowId: "w1" }),
    "Workflow: saved (w1)",
  );
  assert.equal(
    formatWorkflowStatusText({ status: WORKFLOW_SAVE_STATUSES.FAILED, error: "boom" }),
    "Workflow: failed - boom",
  );
});
