import { getSchemaForType } from "../nodes/schemas.js";

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

// Form field creators
function createTextInput(field, value) {
  const input = el("input", "config-form-input");
  input.type = field.type || "text";
  input.value = value ?? field.default ?? "";
  input.placeholder = field.placeholder || "";
  if (field.required) input.required = true;
  return input;
}

function createTextarea(field, value) {
  const textarea = el("textarea", "config-form-textarea");

  // Convert objects/arrays to JSON string for display
  let displayValue = value ?? field.default ?? "";
  if (typeof displayValue === "object" && displayValue !== null) {
    displayValue = JSON.stringify(displayValue, null, 2);
  }

  textarea.value = displayValue;
  textarea.placeholder = field.placeholder || "";
  textarea.rows = field.rows || 3;
  if (field.required) textarea.required = true;
  return textarea;
}

function createSelect(field, value) {
  const select = el("select", "config-form-select");
  for (const option of field.options || []) {
    const opt = el("option");
    opt.value = option;
    opt.textContent = option;
    if (value === option || (!value && option === field.default)) {
      opt.selected = true;
    }
    select.appendChild(opt);
  }
  if (field.required) select.required = true;
  return select;
}

function createNumberInput(field, value) {
  const input = el("input", "config-form-input");
  input.type = "number";
  input.value = value ?? field.default ?? "";
  if (field.min !== undefined) input.min = field.min;
  if (field.max !== undefined) input.max = field.max;
  if (field.step !== undefined) input.step = field.step;
  if (field.required) input.required = true;
  return input;
}

function createCheckbox(field, value) {
  const input = el("input", "config-form-checkbox");
  input.type = "checkbox";
  input.checked = value ?? field.default ?? false;
  return input;
}

function createFormRow(field, config) {
  const row = el("div", "config-form-row");
  const label = el("label", "config-form-label");
  label.textContent = field.label;

  let input;
  switch (field.type) {
    case "text":
    case "url":
      input = createTextInput(field, config[field.key]);
      break;
    case "textarea":
      input = createTextarea(field, config[field.key]);
      break;
    case "select":
      input = createSelect(field, config[field.key]);
      break;
    case "number":
      input = createNumberInput(field, config[field.key]);
      break;
    case "checkbox":
      input = createCheckbox(field, config[field.key]);
      break;
    default:
      input = createTextInput(field, config[field.key]);
  }

  input.dataset.configKey = field.key;
  input.dataset.fieldType = field.type;

  row.appendChild(label);
  row.appendChild(input);

  // Add help text if provided
  if (field.help) {
    const help = el("div", "config-form-help");
    help.textContent = field.help;
    row.appendChild(help);
  }

  return row;
}

export function createNodePropertiesEditor({ rootEl, selectionManager, nodeManager, wireManager }) {
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
  hint.textContent = "Select a node or wire to edit.";

  // Wire properties panel
  const wirePanel = el("div", "wire-properties-panel");
  wirePanel.style.display = "none";

  const wireTitleEl = el("h3", "wire-title");
  wireTitleEl.textContent = "Wire Connection";

  const wireFromRow = el("div", "properties-row");
  const wireFromLabel = el("div", "properties-label");
  wireFromLabel.textContent = "From";
  const wireFromValue = el("div", "properties-value");
  wireFromRow.append(wireFromLabel, wireFromValue);

  const wireToRow = el("div", "properties-row");
  const wireToLabel = el("div", "properties-label");
  wireToLabel.textContent = "To";
  const wireToValue = el("div", "properties-value");
  wireToRow.append(wireToLabel, wireToValue);

  const wireIdRow = el("div", "properties-row");
  const wireIdLabel = el("div", "properties-label");
  wireIdLabel.textContent = "Wire ID";
  const wireIdValue = el("input", "properties-input");
  wireIdValue.type = "text";
  wireIdValue.disabled = true;
  wireIdRow.append(wireIdLabel, wireIdValue);

  const wireDeleteBtn = el("button", "properties-delete");
  wireDeleteBtn.type = "button";
  wireDeleteBtn.textContent = "Delete Connection";

  wirePanel.append(wireTitleEl, wireFromRow, wireToRow, wireIdRow, wireDeleteBtn);

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
  childrenRow.style.display = "none";

  // Configuration form container
  const configFormContainer = el("div", "config-form-container");

  // Advanced JSON section (collapsed by default)
  const advancedSection = el("details", "config-advanced");
  const advancedSummary = el("summary", "config-advanced-summary");
  advancedSummary.textContent = "▶ Advanced (JSON Config)";
  const configTextarea = el("textarea", "properties-textarea");
  advancedSection.append(advancedSummary, configTextarea);

  const actions = el("div", "properties-actions");
  const saveButton = el("button", "properties-save");
  saveButton.type = "button";
  saveButton.textContent = "Save";

  const deleteButton = el("button", "properties-delete");
  deleteButton.type = "button";
  deleteButton.textContent = "Delete Node";

  actions.append(saveButton, deleteButton);

  const errorEl = el("div", "properties-error");

  rootEl.replaceChildren(
    title,
    hint,
    wirePanel,
    idRow,
    typeRow,
    titleRow,
    parentRow,
    childrenRow,
    configFormContainer,
    advancedSection,
    actions,
    errorEl
  );

  let selectedNodeId = null;
  let selectedNode = null;
  let selectedWireId = null;

  function setEnabled(enabled) {
    titleInput.disabled = !enabled;
    saveButton.disabled = !enabled;
    deleteButton.disabled = !enabled;
    const formInputs = configFormContainer.querySelectorAll("input, select, textarea");
    formInputs.forEach(input => {
      input.disabled = !enabled;
    });
  }

  function setError(message) {
    errorEl.textContent = message ? `Error: ${message}` : "";
  }

  // Collect form values into config object
  function collectFormConfig() {
    const config = {};
    const formInputs = configFormContainer.querySelectorAll("[data-config-key]");

    formInputs.forEach(input => {
      const key = input.dataset.configKey;
      const fieldType = input.dataset.fieldType;

      if (fieldType === "checkbox") {
        config[key] = input.checked;
      } else if (fieldType === "number") {
        const val = parseFloat(input.value);
        if (!isNaN(val)) {
          config[key] = val;
        }
      } else if (fieldType === "textarea") {
        // For textareas, try to parse as JSON (for arrays/objects)
        const val = input.value.trim();
        if (val) {
          try {
            // Try parsing as JSON first
            config[key] = JSON.parse(val);
          } catch (e) {
            // If not valid JSON, store as string
            config[key] = val;
          }
        }
      } else {
        const val = input.value.trim();
        if (val) {
          config[key] = val;
        }
      }
    });

    return config;
  }

  // Sync form changes to JSON textarea
  function syncFormToJson() {
    const config = collectFormConfig();
    configTextarea.value = safeStringify(config);
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
      configFormContainer.innerHTML = "";
      configTextarea.value = "";
      setEnabled(false);
      setError("");
      return;
    }

    hint.style.display = "none";
    idInput.value = selectedNode.id;
    typeInput.value = selectedNode.type;
    titleInput.value = selectedNode.title ?? selectedNode.type;

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

    // Build config form based on schema
    const schema = getSchemaForType(selectedNode.type);
    configFormContainer.innerHTML = "";

    if (schema && schema.fields && schema.fields.length > 0) {
      const formTitle = el("div", "config-form-title");
      formTitle.textContent = "Configuration";
      configFormContainer.appendChild(formTitle);

      for (const field of schema.fields) {
        const row = createFormRow(field, selectedNode.config || {});
        configFormContainer.appendChild(row);

        // Add change listener to sync to JSON
        const input = row.querySelector("[data-config-key]");
        if (input) {
          input.addEventListener("input", syncFormToJson);
          input.addEventListener("change", syncFormToJson);
        }
      }
    } else if (selectedNode.type !== "start" && selectedNode.type !== "end") {
      // Show message for nodes without schema
      const noSchema = el("div", "config-form-hint");
      noSchema.textContent = "No form available for this node type. Use JSON config below.";
      configFormContainer.appendChild(noSchema);
    }

    configTextarea.value = safeStringify(selectedNode.config);
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

    // Try to collect from form first
    let config = collectFormConfig();

    // If JSON was manually edited, use that instead
    const jsonText = configTextarea.value.trim();
    if (jsonText) {
      const parsed = parseConfigText(jsonText);
      if (!parsed.ok) {
        setError(parsed.error);
        return;
      }
      // Merge JSON config with form config (JSON takes precedence)
      config = { ...config, ...parsed.value };
    }

    node.title = titleInput.value?.trim() ? titleInput.value.trim() : node.type;
    node.config = config;
    setError("");

    // Update the JSON textarea to reflect merged config
    configTextarea.value = safeStringify(config);
  });

  deleteButton.addEventListener("click", () => {
    if (!selectedNodeId) {
      return;
    }
    const node = nodeManager.getById(selectedNodeId);
    if (!node) {
      loadNode(null);
      return;
    }

    if (confirm(`Delete node "${node.title || node.id}"?`)) {
      nodeManager.removeNode(selectedNodeId);
      loadNode(null);
    }
  });

  selectionManager.setOnSelectionChanged((nextId) => {
    if (nextId === selectedNodeId) {
      return;
    }
    loadNode(nextId);
    if (nextId) {
      // Node selected - hide wire panel
      wirePanel.style.display = "none";
      selectedWireId = null;
    }
  });

  // Wire selection handling
  function loadWire(wireId) {
    selectedWireId = wireId;

    if (!wireId || !wireManager) {
      wirePanel.style.display = "none";
      return;
    }

    const wires = wireManager.getWires();
    const wire = wires.find(w => w.id === wireId);
    if (!wire) {
      wirePanel.style.display = "none";
      return;
    }

    // Hide node properties, show wire properties
    loadNode(null);
    hint.style.display = "none";
    wirePanel.style.display = "block";

    // Populate wire info
    wireIdValue.value = wire.id;

    const fromNode = nodeManager.getById(wire.from.nodeId);
    const toNode = nodeManager.getById(wire.to.nodeId);

    wireFromValue.textContent = fromNode
      ? `${fromNode.title || fromNode.type} (${wire.from.portId})`
      : `${wire.from.nodeId} (${wire.from.portId})`;

    wireToValue.textContent = toNode
      ? `${toNode.title || toNode.type} (${wire.to.portId})`
      : `${wire.to.nodeId} (${wire.to.portId})`;
  }

  if (selectionManager.setOnWireSelectionChanged) {
    selectionManager.setOnWireSelectionChanged((wireId) => {
      loadWire(wireId);
    });
  }

  wireDeleteBtn.addEventListener("click", () => {
    if (!selectedWireId || !wireManager) {
      return;
    }
    if (confirm("Delete this connection?")) {
      wireManager.removeWire(selectedWireId);
      selectionManager.clearWireSelection?.();
      loadWire(null);
      hint.style.display = "block";
    }
  });

  // Initialize from current selection
  loadNode(selectionManager.getSelectedNodeId?.() ?? null);

  return {
    refresh() {
      loadNode(selectedNodeId);
    },
  };
}
