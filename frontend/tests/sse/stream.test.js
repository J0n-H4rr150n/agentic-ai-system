import test from "node:test";
import assert from "node:assert/strict";

import { createSseStream, parseSseJson } from "../../public/js/sse/stream.js";

class FakeEventSource {
  static instances = [];

  constructor(url) {
    this.url = url;
    this.onopen = null;
    this.onerror = null;
    this._listeners = new Map();
    FakeEventSource.instances.push(this);
  }

  addEventListener(name, handler) {
    const list = this._listeners.get(name) ?? [];
    list.push(handler);
    this._listeners.set(name, list);
  }

  emit(name, dataObj) {
    const handlers = this._listeners.get(name) ?? [];
    for (const h of handlers) {
      h({ data: JSON.stringify(dataObj) });
    }
  }

  open() {
    this.onopen?.();
  }

  error(err = new Error("boom")) {
    this.onerror?.(err);
  }

  close() {
    this._closed = true;
  }
}

test("parseSseJson parses valid JSON and throws on invalid", () => {
  assert.deepEqual(parseSseJson("{\"a\":1}"), { a: 1 });
  assert.throws(() => parseSseJson("nope"), /Invalid SSE JSON payload/);
});

test("createSseStream reconnects on error", () => {
  const timeouts = [];
  const setTimeoutImpl = (fn, _ms) => {
    timeouts.push(fn);
    return timeouts.length;
  };
  const clearTimeoutImpl = (_id) => {};

  const events = [];
  const stream = createSseStream({
    url: "/api/run/r1/stream",
    EventSourceImpl: FakeEventSource,
    onEvent: (name, payload) => events.push({ name, payload }),
    setTimeoutImpl,
    clearTimeoutImpl,
    reconnectDelayMs: 1,
    maxReconnectDelayMs: 2,
  });

  stream.connect();
  assert.equal(FakeEventSource.instances.length, 1);

  FakeEventSource.instances[0].error(new Error("network"));
  assert.equal(timeouts.length, 1);

  // Trigger reconnect.
  timeouts[0]();
  assert.equal(FakeEventSource.instances.length, 2);
});
