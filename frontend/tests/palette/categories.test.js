import test from "node:test";
import assert from "node:assert/strict";

import { PALETTE_CATEGORIES } from "../../public/js/palette/categories.js";

test("PALETTE_CATEGORIES has categories with items", () => {
  assert.ok(Array.isArray(PALETTE_CATEGORIES));
  assert.ok(PALETTE_CATEGORIES.length >= 1);

  for (const category of PALETTE_CATEGORIES) {
    assert.equal(typeof category.id, "string");
    assert.equal(typeof category.title, "string");
    assert.ok(Array.isArray(category.items));

    for (const item of category.items) {
      assert.equal(typeof item.type, "string");
      assert.equal(typeof item.title, "string");
    }
  }
});
