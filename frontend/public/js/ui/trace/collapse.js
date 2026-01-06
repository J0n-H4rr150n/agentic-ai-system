export const TRACE_COLLAPSED_CLASS = "workspace--trace-collapsed";

export function setTraceCollapsed(workspaceEl, collapsed) {
  if (!workspaceEl || !workspaceEl.classList) {
    throw new Error("setTraceCollapsed: workspaceEl with classList is required");
  }

  const isCollapsed = Boolean(collapsed);
  if (isCollapsed) {
    workspaceEl.classList.add(TRACE_COLLAPSED_CLASS);
  } else {
    workspaceEl.classList.remove(TRACE_COLLAPSED_CLASS);
  }

  return isCollapsed;
}

export function isTraceCollapsed(workspaceEl) {
  if (!workspaceEl || !workspaceEl.classList || typeof workspaceEl.classList.contains !== "function") {
    throw new Error("isTraceCollapsed: workspaceEl with classList.contains is required");
  }
  return workspaceEl.classList.contains(TRACE_COLLAPSED_CLASS);
}
