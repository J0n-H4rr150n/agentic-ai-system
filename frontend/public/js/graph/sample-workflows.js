import { BaseNode } from "../nodes/base.js";
import { Wire } from "../wires/wire.js";

function portIn(nodeId) {
  return `${nodeId}:in:1`;
}

function portOut(nodeId) {
  return `${nodeId}:out:1`;
}

export function buildSampleSecurityWorkflowGraph() {
  const nodes = [
    {
      id: "sample-start",
      type: "start",
      title: "Start",
      position: { x: 80, y: 80 },
      config: {
        initial_state: {
          target_url: "http://localhost:8000",
        },
      },
    },
    {
      id: "sample-browser",
      type: "browser",
      title: "Browser",
      position: { x: 320, y: 80 },
      config: {
        action: "navigate",
        url_key: "target_url",
        observation_mode: "visual",
        output_key: "browser_output",
      },
    },
    {
      id: "sample-llm",
      type: "llm",
      title: "LLM",
      position: { x: 560, y: 80 },
      config: {
        model: "gemini-1.5-flash",
        prompt: "Analyze the page content for obvious security issues. Return JSON with findings.",
        json_mode: true,
        output_key: "llm_output",
      },
    },
    {
      id: "sample-router",
      type: "router",
      title: "Router",
      position: { x: 800, y: 80 },
      config: {
        routes: [
          {
            id: "route-found",
            when: {
              key: "llm_output.json.findings",
              op: "contains",
              value: "sql",
            },
            next: "sample-end",
          },
        ],
        default_next: "sample-end",
      },
    },
    {
      id: "sample-end",
      type: "end",
      title: "End",
      position: { x: 1040, y: 80 },
      config: {
        result_key: "result",
      },
    },
  ];

  const edges = [
    {
      id: "edge-start-browser",
      from: { nodeId: "sample-start", portId: portOut("sample-start") },
      to: { nodeId: "sample-browser", portId: portIn("sample-browser") },
    },
    {
      id: "edge-browser-llm",
      from: { nodeId: "sample-browser", portId: portOut("sample-browser") },
      to: { nodeId: "sample-llm", portId: portIn("sample-llm") },
    },
    {
      id: "edge-llm-router",
      from: { nodeId: "sample-llm", portId: portOut("sample-llm") },
      to: { nodeId: "sample-router", portId: portIn("sample-router") },
    },
    {
      id: "edge-router-end",
      from: { nodeId: "sample-router", portId: portOut("sample-router") },
      to: { nodeId: "sample-end", portId: portIn("sample-end") },
    },
  ];

  return { version: 1, nodes, edges };
}

export function loadGraphIntoManagers({ graph, nodeManager, wireManager }) {
  if (!graph || typeof graph !== "object") {
    throw new Error("graph is required");
  }
  if (!nodeManager || typeof nodeManager.clear !== "function" || typeof nodeManager.add !== "function") {
    throw new Error("nodeManager must support clear() and add()");
  }
  if (!wireManager || typeof wireManager.clear !== "function" || typeof wireManager.addWire !== "function") {
    throw new Error("wireManager must support clear() and addWire()");
  }

  nodeManager.clear();
  wireManager.clear();

  for (const node of graph.nodes ?? []) {
    nodeManager.add(
      new BaseNode({
        id: node.id,
        type: node.type,
        title: node.title,
        position: node.position,
        size: node.size,
        ports: node.ports,
        config: node.config,
      }),
    );
  }

  for (const edge of graph.edges ?? []) {
    wireManager.addWire(new Wire({ id: edge.id, from: edge.from, to: edge.to }));
  }
}

export function loadSampleSecurityWorkflow({ nodeManager, wireManager }) {
  const graph = buildSampleSecurityWorkflowGraph();

  return loadGraphIntoManagers({ graph, nodeManager, wireManager });
}
