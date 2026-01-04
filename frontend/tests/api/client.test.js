import test from "node:test";
import assert from "node:assert/strict";

import { ApiError, createApiClient } from "../../public/js/api/client.js";

function makeFetch({ status = 200, bodyText = "", headers = {} } = {}) {
  return async (url, _options) => {
    return {
      ok: status >= 200 && status < 300,
      status,
      headers: new Headers(headers),
      async text() {
        return bodyText;
      },
    };
  };
}

test("createApiClient.requestJson returns parsed JSON", async () => {
  const client = createApiClient({ baseUrl: "/api", fetchImpl: makeFetch({ bodyText: "{\"ok\":true}" }) });
  const result = await client.requestJson("/health");
  assert.deepEqual(result, { ok: true });
});

test("createApiClient.requestJson returns null for empty body", async () => {
  const client = createApiClient({ baseUrl: "/api", fetchImpl: makeFetch({ bodyText: "" }) });
  const result = await client.requestJson("/health");
  assert.equal(result, null);
});

test("createApiClient.requestJson throws ApiError on non-2xx", async () => {
  const client = createApiClient({
    baseUrl: "/api",
    fetchImpl: makeFetch({ status: 404, bodyText: "not found" }),
  });

  await assert.rejects(() => client.requestJson("/missing"), (err) => {
    assert.ok(err instanceof ApiError);
    assert.equal(err.status, 404);
    assert.equal(err.bodyText, "not found");
    return true;
  });
});

test("createApiClient.requestJson throws ApiError on invalid JSON", async () => {
  const client = createApiClient({ baseUrl: "/api", fetchImpl: makeFetch({ bodyText: "nope" }) });

  await assert.rejects(() => client.requestJson("/health"), (err) => {
    assert.ok(err instanceof ApiError);
    assert.equal(err.message, "Response was not valid JSON");
    return true;
  });
});
