function el(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function safeStringify(value) {
  try {
    return JSON.stringify(value ?? {}, null, 2);
  } catch {
    return "{}";
  }
}

function parseConfigText(text) {
  const trimmed = String(text ?? "").trim();
  if (!trimmed) {
    return { ok: true, value: {} };
  }
  try {
    const parsed = JSON.parse(trimmed);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { ok: false, error: "Config must be a JSON object (not an array)." };
    }
    return { ok: true, value: parsed };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : "Invalid JSON" };
  }
}

export function createNodePropertiesEditor({ rootEl, selectionManager, nodeManager }) {
  if (!rootEl) {
    throw new Error("createNodePropertiesEditor: rootEl is required");
  }
  if (!selectionManager || typeof selectionManager.setOnSelectionChanged !== "function") {
    throw new Error("createNodePropertiesEditor: selectionManager with setOnSelectionChanged is required");
  }
  if (!nodeManager || typeof nodeManager.getById !== "function") {
    throw new Error("createNodePropertiesEditor: nodeManager with getById is required");
  }

  const title = el("h2", "properties-title");
  title.textContent = "Node Properties";

  const hint = el("div", "properties-hint");
  hint.textContent = "Select a node to edit.";

  const idRow = el("div", "properties-row");
  const idLabel = el("div", "properties-label");
  idLabel.textContent = "Node ID";
  const idInput = el("input", "properties-input");
  idInput.type = "text";
  idInput.disabled = true;
  idRow.append(idLabel, idInput);

  const typeRow = el("div", "properties-row");
  const typeLabel = el("div", "properties-label");
  typeLabel.textContent = "Type";
  const typeInput = el("input", "properties-input");
  typeInput.type = "text";
  typeInput.disabled = true;
  typeRow.append(typeLabel, typeInput);

  const titleRow = el("div", "properties-row");
  const titleLabel = el("div", "properties-label");
  titleLabel.textContent = "Title";
  const titleInput = el("input", "properties-input");
  titleInput.type = "text";
  titleRow.append(titleLabel, titleInput);

  const parentRow = el("div", "properties-row");
  const parentLabel = el("div", "properties-label");
  parentLabel.textContent = "Parent Container";
  const parentInput = el("input", "properties-input");
  parentInput.type = "text";
  parentInput.disabled = true;
  parentInput.placeholder = "None";
  parentRow.append(parentLabel, parentInput);

  const childrenRow = el("div", "properties-row");
  const childrenLabel = el("div", "properties-label");
  childrenLabel.textContent = "Children";
  const childrenList = el("div", "properties-children-list");
  childrenRow.append(childrenLabel, childrenList);
  childrenRow.style.display = "none"; // Hidden by default

  const configRow = el("div", "properties-row");
  const configLabel = el("div", "properties-label");
  configLabel.textContent = "Config (JSON)";
  const configTextarea = el("textarea", "properties-textarea");
  configRow.append(configLabel, configTextarea);

  const actions = el("div", "properties-actions");
  const saveButton = el("button", "properties-save");
  saveButton.type = "button";
  saveButton.textContent = "Save";
  actions.append(saveButton);

  const errorEl = el("div", "properties-error");

  rootEl.replaceChildren(title, hint, idRow, typeRow, titleRow, parentRow, childrenRow, configRow, actions, errorEl);

  let selectedNodeId = null;
  let selectedNode = null;

  function setEnabled(enabled) {
    titleInput.disabled = !enabled;
    configTextarea.disabled = !enabled;
    saveButton.disabled = !enabled;
  }

  function setError(message) {
    errorEl.textContent = message ? `Error: ${message}` : "";
  }

  function loadNode(nodeId) {
    selectedNodeId = nodeId;
    selectedNode = nodeId ? nodeManager.getById(nodeId) : null;

    if (!selectedNode) {
      hint.style.display = "block";
      idInput.value = "";
      typeInput.value = "";
      titleInput.value = "";
      parentInput.value = "";
      parentRow.style.display = "none";
      childrenRow.style.display = "none";
      configTextarea.value = "";
      setEnabled(false);
      setError("");
      return;
    }

    hint.style.display = "none";
    idInput.value = selectedNode.id;
    typeInput.value = selectedNode.type;
    titleInput.value = selectedNode.title ?? selectedNode.type;
    configTextarea.value = safeStringify(selectedNode.config);

    // Show parent container for regular nodes
    if (selectedNode.type === "container") {
      parentRow.style.display = "none";
      childrenRow.style.display = "block";

      // Show children list for containers
      const children = nodeManager.getNodes().filter(n => n.parentId === selectedNode.id);
      if (children.length === 0) {
        childrenList.innerHTML = '<div style="color: var(--text-1); font-size: 11px;">No children</div>';
      } else {
        childrenList.innerHTML = children.map(child =>
          `<div style="padding: 4px 0; font-size: 11px; color: var(--text-0);">• ${child.id} (${child.type})</div>`
        ).join("");
      }
    } else {
      childrenRow.style.display = "none";
      parentRow.style.display = "block";

      // Show parent container name
      if (selectedNode.parentId) {
        const parent = nodeManager.getById(selectedNode.parentId);
        parentInput.value = parent ? `${parent.title || parent.type} (${parent.id})` : selectedNode.parentId;
      } else {
        parentInput.value = "";
      }
    }

    setEnabled(true);
    setError("");
  }

  saveButton.addEventListener("click", () => {
    if (!selectedNodeId) {
      return;
    }
    const node = nodeManager.getById(selectedNodeId);
    if (!node) {
      loadNode(null);
      return;
    }

    const parsed = parseConfigText(configTextarea.value);
    if (!parsed.ok) {
      setError(parsed.error);
      return;
    }

    node.title = titleInput.value?.trim() ? titleInput.value.trim() : node.type;
    node.config = parsed.value;
    setError("");
  });

  selectionManager.setOnSelectionChanged((nextId) => {
    if (nextId === selectedNodeId) {
      return;
    }
    loadNode(nextId);
  });

  // Initialize from current selection.
  loadNode(selectionManager.getSelectedNodeId?.() ?? null);

  return {
    refresh() {
      loadNode(selectedNodeId);
    },
  };
}
