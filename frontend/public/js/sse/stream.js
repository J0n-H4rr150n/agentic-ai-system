/**
 * Parse a JSON `data:` payload from an SSE message.
 * @param {string} data
 */
export function parseSseJson(data) {
  if (typeof data !== "string") {
    throw new Error("data must be a string");
  }
  try {
    return JSON.parse(data);
  } catch {
    throw new Error("Invalid SSE JSON payload");
  }
}

/**
 * Minimal SSE wrapper with reconnect.
 *
 * @param {{
 *   url: string,
 *   EventSourceImpl?: typeof EventSource,
 *   onEvent?: (eventName: string, payload: any) => void,
 *   onOpen?: () => void,
 *   onError?: (err: any) => void,
 *   reconnectDelayMs?: number,
 *   maxReconnectDelayMs?: number,
 *   setTimeoutImpl?: typeof setTimeout,
 *   clearTimeoutImpl?: typeof clearTimeout,
 * }} params
 */
export function createSseStream({
  url,
  EventSourceImpl = EventSource,
  onEvent = () => {},
  onOpen = () => {},
  onError = () => {},
  reconnectDelayMs = 500,
  maxReconnectDelayMs = 5000,
  setTimeoutImpl = setTimeout,
  clearTimeoutImpl = clearTimeout,
}) {
  if (typeof url !== "string" || !url) {
    throw new Error("url must be a non-empty string");
  }
  if (typeof EventSourceImpl !== "function") {
    throw new Error("EventSourceImpl must be a constructor");
  }
  if (typeof onEvent !== "function" || typeof onOpen !== "function" || typeof onError !== "function") {
    throw new Error("callbacks must be functions");
  }

  let closed = false;
  let source = null;
  let reconnectTimer = null;
  let currentDelay = reconnectDelayMs;

  function clearReconnect() {
    if (reconnectTimer !== null) {
      clearTimeoutImpl(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function closeSource() {
    if (source) {
      source.close();
      source = null;
    }
  }

  function scheduleReconnect() {
    if (closed) {
      return;
    }

    clearReconnect();
    reconnectTimer = setTimeoutImpl(() => {
      connectInternal();
    }, currentDelay);

    currentDelay = Math.min(maxReconnectDelayMs, currentDelay * 2);
  }

  function attachHandlers(es) {
    es.onopen = () => {
      currentDelay = reconnectDelayMs;
      onOpen();
    };

    es.onerror = (err) => {
      onError(err);
      closeSource();
      scheduleReconnect();
    };

    for (const eventName of ["hello", "step", "status"]) {
      es.addEventListener(eventName, (e) => {
        const payload = parseSseJson(e.data);
        onEvent(eventName, payload);
      });
    }
  }

  function connectInternal() {
    if (closed) {
      return;
    }

    clearReconnect();
    closeSource();

    const es = new EventSourceImpl(url);
    source = es;
    attachHandlers(es);
  }

  function connect() {
    connectInternal();
    return api;
  }

  function close() {
    closed = true;
    clearReconnect();
    closeSource();
  }

  const api = {
    connect,
    close,
  };

  return api;
}
