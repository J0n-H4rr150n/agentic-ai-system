import test from "node:test";
import assert from "node:assert/strict";

import { WireManager } from "../../public/js/wires/index.js";
import { PORT_KIND } from "../../public/js/nodes/port.js";

test("WireManager.isValidConnection only allows output->input", () => {
  const manager = new WireManager();

  const output = { kind: PORT_KIND.OUTPUT };
  const input = { kind: PORT_KIND.INPUT };

  assert.equal(manager.isValidConnection({ fromPortInfo: output, toPortInfo: input }), true);
  assert.equal(manager.isValidConnection({ fromPortInfo: input, toPortInfo: output }), false);
});
