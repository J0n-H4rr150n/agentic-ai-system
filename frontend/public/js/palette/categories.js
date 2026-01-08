export const PALETTE_CATEGORIES = [
  {
    id: "layout",
    title: "Layout",
    items: [{
      type: "container",
      title: "Container",
      description: "Groups related nodes for organization. Purely visual, no execution logic."
    }],
  },
  {
    id: "control",
    title: "Control",
    items: [
      { type: "start", title: "Start", description: "Entry point for workflow execution. Define initial state variables here." },
      { type: "input", title: "Input", description: "Generic text/string input. Use for workflow parameters like URLs, prompts, or configuration." },
      { type: "end", title: "End", description: "Terminates workflow execution. Optionally specify which state key to return as result." },
      { type: "router", title: "Router", description: "Conditional branching based on state. Routes to different outputs based on conditions." },
      { type: "loop", title: "Loop", description: "Iterates over a nested workflow up to max iterations. Supports break conditions." },
      { type: "parallel_gate", title: "Parallel Gate", description: "Executes multiple paths concurrently and waits for all to complete." },
      { type: "human_approval", title: "Human Approval", description: "Pauses workflow and waits for human approve/reject decision. Shows context from state." },
    ],
  },
  {
    id: "tools",
    title: "Tools",
    items: [
      { type: "browser", title: "Browser", description: "Web automation - navigate, click, screenshot. Supports visual observation and DOM interaction." },
      { type: "llm", title: "LLM", description: "AI reasoning and decision-making. Supports system prompts and structured JSON output schemas." },
      { type: "http_request", title: "HTTP Request", description: "Make HTTP API calls. Supports all methods, headers, and body payloads." },
      { type: "http_fuzzer", title: "HTTP Fuzzer", description: "Security testing tool. Sends multiple variants of requests to discover vulnerabilities." },
      { type: "code_executor", title: "Code Executor", description: "Run Python or JavaScript code. Access workflow state and return results." },
    ],
  },
];

export function getPaletteTitleForType(type) {
  for (const category of PALETTE_CATEGORIES) {
    for (const item of category.items ?? []) {
      if (item.type === type) {
        return item.title;
      }
    }
  }
  return null;
}
