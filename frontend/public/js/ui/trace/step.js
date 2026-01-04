import { buildStepDetailText, getScreenshotBase64FromOutput } from "./detail.js";

function el(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function formatDuration(durationMs) {
  if (typeof durationMs !== "number" || !Number.isFinite(durationMs)) {
    return null;
  }
  return `${Math.round(durationMs)}ms`;
}

function resolveNodeMeta(graphIndex, nodeId) {
  if (!graphIndex || !nodeId) {
    return { title: nodeId, type: null };
  }
  const meta = graphIndex.get(nodeId);
  if (!meta) {
    return { title: nodeId, type: null };
  }
  return {
    title: meta.title || meta.type || nodeId,
    type: meta.type || null,
  };
}

function statusIcon(status) {
  if (status === "completed") return "✓";
  if (status === "failed") return "✕";
  if (status === "running") return "●";
  return "○";
}

export function createStepElement({ step, graphIndex }) {
  const details = document.createElement("details");
  details.className = "trace-step";

  const summary = document.createElement("summary");

  const left = el("div", "trace-step-summary-left");
  const title = el("div", "trace-step-title");

  const meta = resolveNodeMeta(graphIndex, step?.node_id);
  const icon = statusIcon(step?.status);
  title.textContent = `${icon} ${meta.title}`;

  const metaEl = el("div", "trace-step-meta");
  const durationText = formatDuration(step?.duration_ms);
  const metaParts = [];
  if (meta.type) metaParts.push(meta.type);
  if (durationText) metaParts.push(durationText);
  if (step?.status) metaParts.push(String(step.status));
  metaEl.textContent = metaParts.join(" · ");

  left.append(title, metaEl);
  summary.append(left);

  const detail = el("div", "trace-step-detail");

  const { inputText, outputText, errorText } = buildStepDetailText(step);

  const inputTitle = el("div", "trace-step-meta");
  inputTitle.textContent = "Input";
  const inputPre = el("pre", "trace-pre");
  inputPre.textContent = inputText;

  const outputTitle = el("div", "trace-step-meta");
  outputTitle.textContent = "Output";
  const outputPre = el("pre", "trace-pre");
  outputPre.textContent = outputText;

  detail.append(inputTitle, inputPre, outputTitle, outputPre);

  if (errorText) {
    const errorTitle = el("div", "trace-step-meta");
    errorTitle.textContent = "Error";
    const errorPre = el("pre", "trace-pre");
    errorPre.textContent = errorText;
    detail.append(errorTitle, errorPre);
  }

  const screenshotBase64 = getScreenshotBase64FromOutput(step?.output);
  if (screenshotBase64) {
    const wrap = el("div", "trace-screenshot");
    const img = document.createElement("img");
    img.alt = "Step screenshot";

    if (screenshotBase64.startsWith("data:image/")) {
      img.src = screenshotBase64;
    } else {
      img.src = `data:image/png;base64,${screenshotBase64}`;
    }

    wrap.append(img);
    detail.append(wrap);
  }

  details.append(summary, detail);
  return details;
}
