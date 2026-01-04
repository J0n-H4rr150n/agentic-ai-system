import test from "node:test";
import assert from "node:assert/strict";

import { NodeManager } from "../../public/js/nodes/index.js";
import { WireManager } from "../../public/js/wires/index.js";
import {
  buildSampleSecurityWorkflowGraph,
  loadSampleSecurityWorkflow,
} from "../../public/js/graph/sample-workflows.js";

test("buildSampleSecurityWorkflowGraph returns Start→Browser→LLM→Router→End", () => {
  const graph = buildSampleSecurityWorkflowGraph();

  const types = graph.nodes.map((n) => n.type);
  assert.deepEqual(types, ["start", "browser", "llm", "router", "end"]);

  assert.equal(graph.edges.length, 4);
  assert.deepEqual(
    graph.edges.map((e) => `${e.from.nodeId}->${e.to.nodeId}`),
    [
      "sample-start->sample-browser",
      "sample-browser->sample-llm",
      "sample-llm->sample-router",
      "sample-router->sample-end",
    ],
  );
});

test("loadSampleSecurityWorkflow populates node and wire managers", () => {
  const nodeManager = new NodeManager();
  const wireManager = new WireManager();

  loadSampleSecurityWorkflow({ nodeManager, wireManager });

  assert.equal(nodeManager.getNodes().length, 5);
  assert.equal(wireManager.getWires().length, 4);

  const nodeIds = new Set(nodeManager.getNodes().map((n) => n.id));
  for (const expected of ["sample-start", "sample-browser", "sample-llm", "sample-router", "sample-end"]) {
    assert.ok(nodeIds.has(expected));
  }
});
