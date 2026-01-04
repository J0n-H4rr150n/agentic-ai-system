/**
 * Build palette categories including a "Saved Agents" section.
 *
 * This is display-only in F00006_S004: saved workflows are not draggable/executable yet.
 *
 * @param {{
 *  categories: Array<{ id: string, title: string, items: Array<{ type: string, title: string }> }>,
 *  workflows: Array<{ workflow_id: string, latest_version: number }> | null | undefined,
 * }} params
 */
export function buildPaletteCategoriesWithSavedAgents({ categories, workflows }) {
  const base = Array.isArray(categories) ? categories : [];
  const list = Array.isArray(workflows) ? workflows : [];

  if (!list.length) {
    return base;
  }

  const savedItems = list
    .filter((w) => w && typeof w.workflow_id === "string" && w.workflow_id)
    .map((w) => {
      const latestVersion = typeof w.latest_version === "number" && Number.isFinite(w.latest_version) ? w.latest_version : 0;
      const shortId = w.workflow_id.length > 8 ? w.workflow_id.slice(0, 8) : w.workflow_id;

      return {
        // Empty type ensures PaletteDragDropHandler ignores the item.
        type: "",
        title: latestVersion > 0 ? `Agent ${shortId} (v${latestVersion})` : `Agent ${shortId}`,
      };
    });

  if (!savedItems.length) {
    return base;
  }

  return [
    ...base,
    {
      id: "saved-agents",
      title: "Saved Agents",
      items: savedItems,
    },
  ];
}
