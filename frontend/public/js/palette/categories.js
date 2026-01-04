export const PALETTE_CATEGORIES = [
  {
    id: "layout",
    title: "Layout",
    items: [{ type: "container", title: "Container" }],
  },
  {
    id: "control",
    title: "Control",
    items: [
      { type: "start", title: "Start" },
      { type: "end", title: "End" },
      { type: "router", title: "Router" },
    ],
  },
  {
    id: "tools",
    title: "Tools",
    items: [
      { type: "browser", title: "Browser" },
      { type: "llm", title: "LLM" },
      { type: "http", title: "HTTP Request" },
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
