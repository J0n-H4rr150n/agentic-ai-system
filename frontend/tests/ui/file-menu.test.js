import test from "node:test";
import assert from "node:assert/strict";

import { createFileMenuController } from "../../public/js/ui/file-menu.js";

function createFakeElement(tag) {
  const classSet = new Set();

  const el = {
    tag,
    value: "",
    textContent: "",
    disabled: false,
    children: [],
    _listeners: new Map(),
    _attrs: new Map(),
    classList: {
      add: (c) => classSet.add(c),
      remove: (c) => classSet.delete(c),
      toggle: (c, force) => {
        if (typeof force === "boolean") {
          if (force) classSet.add(c);
          else classSet.delete(c);
          return force;
        }
        if (classSet.has(c)) {
          classSet.delete(c);
          return false;
        }
        classSet.add(c);
        return true;
      },
      contains: (c) => classSet.has(c),
    },
    setAttribute: (k, v) => {
      el._attrs.set(k, String(v));
    },
    getAttribute: (k) => el._attrs.get(k) ?? null,
    appendChild: (child) => {
      el.children.push(child);
      return child;
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
        return handler({ type: event });
      }
      return undefined;
    },
  };

  return el;
}

function createFakeDocument() {
  return {
    createElement: (tag) => createFakeElement(tag),
  };
}

async function flushMicrotasks() {
  await Promise.resolve();
  await Promise.resolve();
}

test("file menu toggles open/closed", async () => {
  const document = createFakeDocument();

  const buttonEl = createFakeElement("button");
  const menuEl = createFakeElement("div");
  const workflowSelectEl = createFakeElement("select");
  const loadWorkflowButtonEl = createFakeElement("button");
  const exportJsonButtonEl = createFakeElement("button");

  const controller = createFileMenuController({
    document,
    buttonEl,
    menuEl,
    workflowSelectEl,
    loadWorkflowButtonEl,
    exportJsonButtonEl,
    workflowApi: {
      listWorkflows: async () => ({ workflows: [] }),
      getWorkflow: async () => ({ graph: { version: 1, nodes: [], edges: [] } }),
    },
    onImportGraph: () => {},
    onWorkflowLoaded: () => {},
    onExportJson: () => {},
  });

  assert.equal(controller.isOpen(), false);
  assert.equal(menuEl.classList.contains("file-menu--open"), false);
  assert.equal(buttonEl.getAttribute("aria-expanded"), "false");

  buttonEl.dispatch("click");
  await flushMicrotasks();

  assert.equal(controller.isOpen(), true);
  assert.equal(menuEl.classList.contains("file-menu--open"), true);
  assert.equal(buttonEl.getAttribute("aria-expanded"), "true");

  buttonEl.dispatch("click");
  await flushMicrotasks();

  assert.equal(controller.isOpen(), false);
  assert.equal(menuEl.classList.contains("file-menu--open"), false);
  assert.equal(buttonEl.getAttribute("aria-expanded"), "false");
});

test("file menu loads workflows list on open", async () => {
  const document = createFakeDocument();

  const buttonEl = createFakeElement("button");
  const menuEl = createFakeElement("div");
  const workflowSelectEl = createFakeElement("select");
  const loadWorkflowButtonEl = createFakeElement("button");
  const exportJsonButtonEl = createFakeElement("button");

  let listCalls = 0;

  createFileMenuController({
    document,
    buttonEl,
    menuEl,
    workflowSelectEl,
    loadWorkflowButtonEl,
    exportJsonButtonEl,
    workflowApi: {
      listWorkflows: async () => {
        listCalls += 1;
        return {
          workflows: [
            { workflow_id: "w1", latest_version: 2 },
            { workflow_id: "w2", latest_version: 1 },
          ],
        };
      },
      getWorkflow: async () => ({ graph: { version: 1, nodes: [], edges: [] } }),
    },
    onImportGraph: () => {},
    onWorkflowLoaded: () => {},
    onExportJson: () => {},
  });

  buttonEl.dispatch("click");
  await flushMicrotasks();

  assert.equal(listCalls, 1);
  assert.equal(workflowSelectEl.disabled, false);
  assert.equal(loadWorkflowButtonEl.disabled, false);
  assert.equal(workflowSelectEl.children.length, 2);
  assert.equal(workflowSelectEl.children[0].value, "w1");
  assert.equal(workflowSelectEl.children[0].textContent, "w1 (v2)");
});

test("load workflow imports graph and reports selected workflow id", async () => {
  const document = createFakeDocument();

  const buttonEl = createFakeElement("button");
  const menuEl = createFakeElement("div");
  const workflowSelectEl = createFakeElement("select");
  const loadWorkflowButtonEl = createFakeElement("button");
  const exportJsonButtonEl = createFakeElement("button");

  /** @type {any[]} */
  const imported = [];
  /** @type {string[]} */
  const loadedIds = [];

  const controller = createFileMenuController({
    document,
    buttonEl,
    menuEl,
    workflowSelectEl,
    loadWorkflowButtonEl,
    exportJsonButtonEl,
    workflowApi: {
      listWorkflows: async () => ({ workflows: [{ workflow_id: "w1", latest_version: 1 }] }),
      getWorkflow: async (workflowId) => ({
        workflow_id: workflowId,
        version: 1,
        graph: { version: 1, nodes: [{ id: "n1", type: "start" }], edges: [] },
      }),
    },
    onImportGraph: (graph) => imported.push(graph),
    onWorkflowLoaded: (workflowId) => loadedIds.push(workflowId),
    onExportJson: () => {},
    onResetUi: () => {},
  });

  controller.open();
  await flushMicrotasks();

  // Select and load.
  workflowSelectEl.value = "w1";
  await controller.loadSelectedWorkflow();

  assert.equal(imported.length, 1);
  assert.equal(imported[0].version, 1);
  assert.deepEqual(loadedIds, ["w1"]);
  assert.equal(menuEl.classList.contains("file-menu--open"), false);
});

test("export json calls provided callback and closes menu", async () => {
  const document = createFakeDocument();

  const buttonEl = createFakeElement("button");
  const menuEl = createFakeElement("div");
  const workflowSelectEl = createFakeElement("select");
  const loadWorkflowButtonEl = createFakeElement("button");
  const exportJsonButtonEl = createFakeElement("button");

  let exports = 0;

  createFileMenuController({
    document,
    buttonEl,
    menuEl,
    workflowSelectEl,
    loadWorkflowButtonEl,
    exportJsonButtonEl,
    workflowApi: {
      listWorkflows: async () => ({ workflows: [] }),
      getWorkflow: async () => ({ graph: { version: 1, nodes: [], edges: [] } }),
    },
    onImportGraph: () => {},
    onWorkflowLoaded: () => {},
    onExportJson: () => {
      exports += 1;
    },
  });

  buttonEl.dispatch("click");
  await flushMicrotasks();

  assert.equal(menuEl.classList.contains("file-menu--open"), true);

  exportJsonButtonEl.dispatch("click");

  assert.equal(exports, 1);
  assert.equal(menuEl.classList.contains("file-menu--open"), false);
});
