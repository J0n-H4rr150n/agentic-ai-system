export class ApiError extends Error {
  /**
   * @param {string} message
   * @param {{ status: number, url: string, bodyText: string | null }} details
   */
  constructor(message, { status, url, bodyText }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.url = url;
    this.bodyText = bodyText;
  }
}

function normalizeBaseUrl(baseUrl) {
  if (typeof baseUrl !== "string" || !baseUrl) {
    throw new Error("baseUrl must be a non-empty string");
  }
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

function buildUrl({ baseUrl, path, query }) {
  const base = normalizeBaseUrl(baseUrl);
  const normalizedPath = typeof path === "string" && path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${base}${normalizedPath}`, "http://localhost");

  if (query && typeof query === "object") {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) {
        continue;
      }
      url.searchParams.set(key, String(value));
    }
  }

  // If baseUrl is absolute, URL(...) will preserve it; if it's relative (e.g. "/api"),
  // strip the dummy origin.
  return base.startsWith("http") ? url.toString() : `${url.pathname}${url.search}`;
}

/**
 * @param {{ baseUrl?: string, fetchImpl?: typeof fetch }} [options]
 */
export function createApiClient(options = {}) {
  const baseUrl = options.baseUrl ?? "/api";
  const fetchImpl = options.fetchImpl ?? fetch;

  if (typeof fetchImpl !== "function") {
    throw new Error("fetchImpl must be a function");
  }

  async function request(path, { method = "GET", headers = {}, query, json, signal } = {}) {
    const url = buildUrl({ baseUrl, path, query });

    const finalHeaders = new Headers(headers);
    let body;

    if (json !== undefined) {
      finalHeaders.set("Content-Type", "application/json");
      body = JSON.stringify(json);
    }

    const response = await fetchImpl(url, {
      method,
      headers: finalHeaders,
      body,
      signal,
    });

    const bodyText = await safeReadText(response);

    if (!response.ok) {
      throw new ApiError(`Request failed: ${response.status}`, {
        status: response.status,
        url,
        bodyText,
      });
    }

    return {
      status: response.status,
      headers: response.headers,
      bodyText,
    };
  }

  async function requestJson(path, options) {
    const result = await request(path, options);
    if (!result.bodyText) {
      return null;
    }

    try {
      return JSON.parse(result.bodyText);
    } catch {
      throw new ApiError("Response was not valid JSON", {
        status: result.status,
        url: buildUrl({ baseUrl, path, query: options?.query }),
        bodyText: result.bodyText,
      });
    }
  }

  return {
    request,
    requestJson,
  };
}

async function safeReadText(response) {
  try {
    const text = await response.text();
    return typeof text === "string" && text.length ? text : null;
  } catch {
    return null;
  }
}
