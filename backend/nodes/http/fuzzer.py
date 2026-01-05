"""HTTP fuzzer node.

This node expands a URL template with a list of payloads and executes a batch
of HTTP requests, returning aggregated results for downstream analysis.

MVP contract:
- Use `{payload}` substitution in the URL template.
- No built-in LLM loop; downstream nodes can analyze results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

import httpx

from backend.nodes.base import BaseNode
from backend.nodes.http.request import _parse_response_body, _validate_headers


HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


@dataclass(frozen=True, slots=True)
class HTTPFuzzerNodeConfig:
    method: HTTPMethod
    output_key: str = "http_fuzzer_output"

    url_template: str | None = None
    url_template_key: str | None = None

    payloads: list[str] | None = None
    payloads_key: str | None = None

    headers: dict[str, str] | None = None
    headers_key: str | None = None

    timeout_seconds: float = 30.0


class HTTPFuzzerNode(BaseNode):
    """Batch HTTP requester using a payload-expanded URL template."""

    def __init__(
        self,
        node_id: str,
        *,
        client_factory: Callable[[], httpx.AsyncClient] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="http_fuzzer")
        self._config = dict(config or {})
        self._client_factory = client_factory or (lambda: httpx.AsyncClient())

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = self._parse_config(self._config)

        url_template = self._resolve_url_template(cfg, state)
        if "{payload}" not in url_template:
            raise ValueError("HTTPFuzzerNode url_template must include '{payload}'")

        payloads = self._resolve_payloads(cfg, state)
        headers = self._resolve_headers(cfg, state)

        timeout = httpx.Timeout(cfg.timeout_seconds)

        results: list[dict[str, Any]] = []
        async with self._client_factory() as client:
            for payload in payloads:
                url = url_template.replace("{payload}", payload)
                try:
                    response = await client.request(
                        method=cfg.method,
                        url=url,
                        headers=headers,
                        timeout=timeout,
                    )
                    results.append(
                        {
                            "payload": payload,
                            "ok": True,
                            "status": int(response.status_code),
                            "headers": dict(response.headers),
                            "body": _parse_response_body(response),
                        }
                    )
                except httpx.RequestError as exc:
                    results.append({"payload": payload, "ok": False, "error": str(exc)})

        ok_count = sum(1 for r in results if r.get("ok") is True)
        out = {
            "method": cfg.method,
            "url_template": url_template,
            "results": results,
            "summary": {"total": len(results), "ok": ok_count, "error": len(results) - ok_count},
        }

        return {cfg.output_key: out}

    @staticmethod
    def _parse_config(raw: dict[str, Any]) -> HTTPFuzzerNodeConfig:
        method = raw.get("method")
        if method not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
            raise ValueError(
                "HTTPFuzzerNode config.method must be one of: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS"
            )

        output_key = raw.get("output_key", "http_fuzzer_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("HTTPFuzzerNode config.output_key must be a non-empty string")

        timeout_seconds = raw.get("timeout_seconds", 30.0)
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("HTTPFuzzerNode config.timeout_seconds must be a positive number")

        headers = raw.get("headers")
        if headers is not None:
            headers = _validate_headers(headers)

        payloads = raw.get("payloads")
        if payloads is not None:
            if not isinstance(payloads, list) or any(not isinstance(p, str) for p in payloads):
                raise ValueError("HTTPFuzzerNode config.payloads must be a list of strings")

        return HTTPFuzzerNodeConfig(
            method=method,
            output_key=output_key,
            url_template=raw.get("url_template"),
            url_template_key=raw.get("url_template_key"),
            payloads=payloads,
            payloads_key=raw.get("payloads_key"),
            headers=headers,
            headers_key=raw.get("headers_key"),
            timeout_seconds=float(timeout_seconds),
        )

    @staticmethod
    def _resolve_url_template(cfg: HTTPFuzzerNodeConfig, state: dict[str, Any]) -> str:
        if cfg.url_template is not None:
            if not isinstance(cfg.url_template, str) or not cfg.url_template.strip():
                raise ValueError("HTTPFuzzerNode config.url_template must be a non-empty string")
            return cfg.url_template

        if cfg.url_template_key is None:
            raise ValueError("HTTPFuzzerNode requires config.url_template or config.url_template_key")
        if not isinstance(cfg.url_template_key, str) or not cfg.url_template_key:
            raise ValueError("HTTPFuzzerNode config.url_template_key must be a non-empty string")

        value = state.get(cfg.url_template_key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"HTTPFuzzerNode state[{cfg.url_template_key!r}] must be a non-empty string")
        return value

    @staticmethod
    def _resolve_payloads(cfg: HTTPFuzzerNodeConfig, state: dict[str, Any]) -> list[str]:
        if cfg.payloads is not None:
            if not cfg.payloads:
                raise ValueError("HTTPFuzzerNode config.payloads must be non-empty")
            return list(cfg.payloads)

        if cfg.payloads_key is None:
            raise ValueError("HTTPFuzzerNode requires config.payloads or config.payloads_key")
        if not isinstance(cfg.payloads_key, str) or not cfg.payloads_key:
            raise ValueError("HTTPFuzzerNode config.payloads_key must be a non-empty string")

        value = state.get(cfg.payloads_key)
        if not isinstance(value, list) or any(not isinstance(p, str) for p in value):
            raise ValueError(f"HTTPFuzzerNode state[{cfg.payloads_key!r}] must be a list of strings")
        if not value:
            raise ValueError(f"HTTPFuzzerNode state[{cfg.payloads_key!r}] must be non-empty")
        return list(value)

    @staticmethod
    def _resolve_headers(cfg: HTTPFuzzerNodeConfig, state: dict[str, Any]) -> dict[str, str] | None:
        if cfg.headers is not None:
            return dict(cfg.headers)

        if cfg.headers_key is None:
            return None
        if not isinstance(cfg.headers_key, str) or not cfg.headers_key:
            raise ValueError("HTTPFuzzerNode config.headers_key must be a non-empty string")

        value = state.get(cfg.headers_key)
        if value is None:
            return None
        return _validate_headers(value)


NODE_TYPE = "http_fuzzer"
NODE_CLASS = HTTPFuzzerNode
