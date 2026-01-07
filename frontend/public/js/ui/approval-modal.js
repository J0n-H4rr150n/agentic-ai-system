function el(tag, className) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  return node;
}

function formatCountdown(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  const mins = Math.floor(s / 60);
  const secs = s % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
}

export function showApprovalModal({ title, message, contextEntries, timeoutSeconds }) {
  const overlay = el("div", "approval-overlay");
  const dialog = el("div", "approval-dialog");

  const h = el("h2", "approval-title");
  h.textContent = title;

  const p = el("p", "approval-message");
  p.textContent = message;

  dialog.appendChild(h);
  dialog.appendChild(p);

  if (Array.isArray(contextEntries) && contextEntries.length > 0) {
    const ctxHeader = el("h3", "approval-context-title");
    ctxHeader.textContent = "Context";

    const list = el("ul", "approval-context");
    for (const item of contextEntries) {
      const li = el("li", "approval-context-item");
      li.textContent = `${item.key}: ${item.valueText}`;
      list.appendChild(li);
    }

    dialog.appendChild(ctxHeader);
    dialog.appendChild(list);
  }

  const footer = el("div", "approval-footer");
  const countdown = el("div", "approval-countdown");

  const actions = el("div", "approval-actions");
  const approveBtn = el("button", "approval-btn approval-btn-approve");
  approveBtn.type = "button";
  approveBtn.textContent = "Approve";

  const rejectBtn = el("button", "approval-btn approval-btn-reject");
  rejectBtn.type = "button";
  rejectBtn.textContent = "Reject";

  actions.appendChild(approveBtn);
  actions.appendChild(rejectBtn);

  footer.appendChild(countdown);
  footer.appendChild(actions);

  dialog.appendChild(footer);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  return new Promise((resolve) => {
    let remaining = typeof timeoutSeconds === "number" && timeoutSeconds > 0 ? timeoutSeconds : null;
    let interval = null;
    let timeout = null;

    function cleanup(result) {
      if (interval) clearInterval(interval);
      if (timeout) clearTimeout(timeout);
      overlay.remove();
      resolve(result);
    }

    approveBtn.addEventListener("click", () => cleanup(true));
    rejectBtn.addEventListener("click", () => cleanup(false));

    if (remaining !== null) {
      countdown.textContent = `Auto-rejects in: ${formatCountdown(remaining)}`;
      interval = setInterval(() => {
        remaining -= 1;
        countdown.textContent = `Auto-rejects in: ${formatCountdown(remaining)}`;
        if (remaining <= 0) {
          clearInterval(interval);
          interval = null;
        }
      }, 1000);

      timeout = setTimeout(() => cleanup(false), remaining * 1000);
    } else {
      countdown.textContent = "";
    }
  });
}
