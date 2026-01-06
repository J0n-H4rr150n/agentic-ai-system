import test from "node:test";
import assert from "node:assert/strict";

import { createNodePropertiesEditor } from "../../public/js/ui/node-properties.js";

function createFakeElement(tag) {
  const el = {
    tag,
    className: "",
    textContent: "",
    type: "",
    disabled: false,
    value: "",
    style: { display: "" },
    children: [],
    _listeners: new Map(),
    append: (...nodes) => {
      el.children.push(...nodes);
    },
    replaceChildren: (...nodes) => {
      el.children = [...nodes];
    },
    addEventListener: (event, handler) => {
      el._listeners.set(event, handler);
    },
    dispatch: (event) => {
      const handler = el._listeners.get(event);
      if (typeof handler === "function") {
        handler({ type: event });
      }
    },
  };
  return el;
}

function findAllByClass(root, className) {
  const results = [];
  function walk(node) {
    if (!node || typeof node !== "object") return;
    if (node.className === className) {
      results.push(node);
    }
    const children = Array.isArray(node.children) ? node.children : [];
    for (const child of children) {
      walk(child);
    }
  }
  walk(root);
  return results;
}

function findByTagAndClass(root, tag, className) {
  return (
    findAllByClass(root, className).find((n) => n.tag === tag) ?? null
  );
}

function createSelectionManager() {
  let selected = null;
  let callback = null;

  return {
    getSelectedNodeId: () => selected,
    setOnSelectionChanged: (cb) => {
      callback = cb;
    },
    select: (nextId) => {
      selected = nextId;
      if (typeof callback === "function") {
        callback(selected);
      }
    },
  };
}

test("node properties editor shows disabled state when nothing selected", () => {
  global.document = {
    createElement: (tag) => createFakeElement(tag),
  };

  const rootEl = createFakeElement("div");
  const selectionManager = createSelectionManager();
  const nodeManager = { getById: () => null };

  createNodePropertiesEditor({ rootEl, selectionManager, nodeManager });

  const hint = findByTagAndClass(rootEl, "div", "properties-hint");
  assert.ok(hint);
  assert.equal(hint.style.display, "block");

  const titleInput = findAllByClass(rootEl, "properties-input")[2];
  assert.ok(titleInput);
  assert.equal(titleInput.disabled, true);

  const textarea = findByTagAndClass(rootEl, "textarea", "properties-textarea");
  assert.ok(textarea);
  assert.equal(textarea.disabled, true);
});

test("node properties editor loads selected node and saves title/config", () => {
  global.document = {
    createElement: (tag) => createFakeElement(tag),
  };

  const rootEl = createFakeElement("div");
  const selectionManager = createSelectionManager();

  const node = {
    id: "n1",
    type: "http_request",
    title: "Old",
    config: { url: "https://example.com" },
  };

  const nodeManager = {
    getById: (id) => (id === "n1" ? node : null),
  };

  createNodePropertiesEditor({ rootEl, selectionManager, nodeManager });

  selectionManager.select("n1");

  const hint = findByTagAndClass(rootEl, "div", "properties-hint");
  assert.ok(hint);
  assert.equal(hint.style.display, "none");

  const inputs = findAllByClass(rootEl, "properties-input");
  assert.equal(inputs.length >= 3, true);

  const idInput = inputs[0];
  const typeInput = inputs[1];
  const titleInput = inputs[2];

  assert.equal(idInput.value, "n1");
  assert.equal(typeInput.value, "http_request");
  assert.equal(titleInput.value, "Old");

  const textarea = findByTagAndClass(rootEl, "textarea", "properties-textarea");
  assert.ok(textarea);

  // Invalid JSON should show an error and not apply changes.
  titleInput.value = "New Title";
  textarea.value = "{ invalid json";

  const saveButton = findByTagAndClass(rootEl, "button", "properties-save");
  assert.ok(saveButton);
  saveButton.dispatch("click");

  const errorEl = findByTagAndClass(rootEl, "div", "properties-error");
  assert.ok(errorEl);
  assert.match(errorEl.textContent, /Error:/);
  assert.equal(node.title, "Old");

  // Valid JSON should apply.
  textarea.value = JSON.stringify({ method: "GET" });
  saveButton.dispatch("click");

  assert.equal(errorEl.textContent, "");
  assert.equal(node.title, "New Title");
  assert.deepEqual(node.config, { method: "GET" });
});
