"""HTTP request node.

Implements a minimal outbound HTTP node for the MVP.

Config supports:
- method: GET/POST/PUT/DELETE/PATCH
- url or url_key
- headers or headers_key
- json_body or json_body_key
- form_body or form_body_key

Output captures:
- status
- headers
- body (json if possible, otherwise text)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

import httpx

from backend.nodes.base import BaseNode


HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]


@dataclass(frozen=True, slots=True)
class HTTPRequestNodeConfig:
    method: HTTPMethod
    output_key: str = "http_output"

    url: str | None = None
    url_key: str | None = None

    headers: dict[str, str] | None = None
    headers_key: str | None = None

    json_body: Any | None = None
    json_body_key: str | None = None

    form_body: dict[str, Any] | None = None
    form_body_key: str | None = None

    timeout_seconds: float = 30.0


class HTTPRequestNode(BaseNode):
    """Node that makes an outbound HTTP request using httpx."""

    def __init__(
        self,
        node_id: str,
        *,
        client_factory: Callable[[], httpx.AsyncClient] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="http_request")
        self._config = dict(config or {})
        self._client_factory = client_factory or (lambda: httpx.AsyncClient())

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = self._parse_config(self._config)

        url = self._resolve_url(cfg, state)
        headers = self._resolve_headers(cfg, state)
        json_body, form_body = self._resolve_body(cfg, state)

        timeout = httpx.Timeout(cfg.timeout_seconds)
        async with self._client_factory() as client:
            response = await client.request(
                method=cfg.method,
                url=url,
                headers=headers,
                json=json_body,
                data=form_body,
                timeout=timeout,
            )

        payload = {
            "method": cfg.method,
            "url": str(response.request.url),
            "status": int(response.status_code),
            "headers": dict(response.headers),
            "body": _parse_response_body(response),
        }

        return {cfg.output_key: payload}

    @staticmethod
    def _parse_config(raw: dict[str, Any]) -> HTTPRequestNodeConfig:
        method = raw.get("method")
        if method not in {"GET", "POST", "PUT", "DELETE", "PATCH"}:
            raise ValueError("HTTPRequestNode config.method must be one of: GET, POST, PUT, DELETE, PATCH")

        output_key = raw.get("output_key", "http_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("HTTPRequestNode config.output_key must be a non-empty string")

        timeout_seconds = raw.get("timeout_seconds", 30.0)
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("HTTPRequestNode config.timeout_seconds must be a positive number")

        headers = raw.get("headers")
        if headers is not None:
            headers = _validate_headers(headers)

        form_body = raw.get("form_body")
        if form_body is not None:
            if not isinstance(form_body, dict):
                raise ValueError("HTTPRequestNode config.form_body must be a dict")

        return HTTPRequestNodeConfig(
            method=method,
            output_key=output_key,
            url=raw.get("url"),
            url_key=raw.get("url_key"),
            headers=headers,
            headers_key=raw.get("headers_key"),
            json_body=raw.get("json_body"),
            json_body_key=raw.get("json_body_key"),
            form_body=form_body,
            form_body_key=raw.get("form_body_key"),
            timeout_seconds=float(timeout_seconds),
        )

    @staticmethod
    def _resolve_url(cfg: HTTPRequestNodeConfig, state: dict[str, Any]) -> str:
        if cfg.url is not None:
            if not isinstance(cfg.url, str) or not cfg.url.strip():
                raise ValueError("HTTPRequestNode config.url must be a non-empty string")
            return cfg.url

        if cfg.url_key is None:
            raise ValueError("HTTPRequestNode requires config.url or config.url_key")
        if not isinstance(cfg.url_key, str) or not cfg.url_key:
            raise ValueError("HTTPRequestNode config.url_key must be a non-empty string")

        value = state.get(cfg.url_key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"HTTPRequestNode state[{cfg.url_key!r}] must be a non-empty string")
        return value

    @staticmethod
    def _resolve_headers(cfg: HTTPRequestNodeConfig, state: dict[str, Any]) -> dict[str, str] | None:
        if cfg.headers is not None:
            return dict(cfg.headers)

        if cfg.headers_key is None:
            return None
        if not isinstance(cfg.headers_key, str) or not cfg.headers_key:
            raise ValueError("HTTPRequestNode config.headers_key must be a non-empty string")

        value = state.get(cfg.headers_key)
        if value is None:
            return None
        return _validate_headers(value)

    @staticmethod
    def _resolve_body(cfg: HTTPRequestNodeConfig, state: dict[str, Any]) -> tuple[Any | None, dict[str, Any] | None]:
        json_body = cfg.json_body
        if cfg.json_body_key is not None:
            if not isinstance(cfg.json_body_key, str) or not cfg.json_body_key:
                raise ValueError("HTTPRequestNode config.json_body_key must be a non-empty string")
            json_body = state.get(cfg.json_body_key)

        form_body = cfg.form_body
        if cfg.form_body_key is not None:
            if not isinstance(cfg.form_body_key, str) or not cfg.form_body_key:
                raise ValueError("HTTPRequestNode config.form_body_key must be a non-empty string")
            value = state.get(cfg.form_body_key)
            if value is None:
                form_body = None
            else:
                if not isinstance(value, dict):
                    raise ValueError(f"HTTPRequestNode state[{cfg.form_body_key!r}] must be a dict")
                form_body = value

        if json_body is not None and form_body is not None:
            raise ValueError("HTTPRequestNode cannot send both json_body and form_body")

        return json_body, form_body


def _validate_headers(headers: Any) -> dict[str, str]:
    if not isinstance(headers, dict):
        raise ValueError("headers must be a dict")

    out: dict[str, str] = {}
    for k, v in headers.items():
        if not isinstance(k, str) or not k:
            raise ValueError("header names must be non-empty strings")
        if not isinstance(v, str):
            raise ValueError("header values must be strings")
        out[k] = v

    return out


def _parse_response_body(response: httpx.Response) -> Any:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type.lower():
        try:
            return response.json()
        except ValueError:
            return response.text

    # Best-effort JSON parse for APIs that return JSON with missing content-type.
    text = response.text
    if text and text.lstrip().startswith(("{", "[")):
        try:
            return response.json()
        except ValueError:
            return text

    return text


NODE_TYPE = "http_request"
NODE_CLASS = HTTPRequestNode
