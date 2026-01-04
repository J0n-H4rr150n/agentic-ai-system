import test from "node:test";
import assert from "node:assert/strict";

import { buildPaletteCategoriesWithSavedAgents } from "../../public/js/palette/saved-agents.js";

test("buildPaletteCategoriesWithSavedAgents returns base categories when no workflows", () => {
  const base = [{ id: "control", title: "Control", items: [{ type: "start", title: "Start" }] }];
  const result = buildPaletteCategoriesWithSavedAgents({ categories: base, workflows: [] });
  assert.equal(result, base);
});

test("buildPaletteCategoriesWithSavedAgents appends Saved Agents category", () => {
  const base = [{ id: "control", title: "Control", items: [{ type: "start", title: "Start" }] }];

  const result = buildPaletteCategoriesWithSavedAgents({
    categories: base,
    workflows: [
      { workflow_id: "abcdef012345", latest_version: 2 },
      { workflow_id: "w2", latest_version: 1 },
    ],
  });

  assert.equal(result.length, 2);
  assert.equal(result[0].id, "control");
  assert.equal(result[1].id, "saved-agents");
  assert.equal(result[1].title, "Saved Agents");
  assert.equal(result[1].items.length, 2);

  // Display-only: empty type so drag handler ignores it.
  assert.equal(result[1].items[0].type, "");
  assert.match(result[1].items[0].title, /Agent abcdef01/);
  assert.match(result[1].items[0].title, /v2/);
});
