"""Browser node.

A minimal `browser` node that performs navigation/click/type actions.

This node uses `BrowserSessionManager` for per-run session reuse, but does not
create Playwright sessions itself. Callers must provide a `session_factory` that
returns a `BrowserSession` whose `context` is a page-like object.

Because the runner does not yet pass a run-scoped context object into nodes,
`run_id` is provided at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from backend.nodes.base import BaseNode
from backend.nodes.browser.actions import BrowserActionResult, BrowserPageLike, click, navigate, resolve_selector, type_text
from backend.nodes.browser.session import BrowserSession, BrowserSessionManager


BrowserAction = Literal["navigate", "click", "type"]


@dataclass(frozen=True, slots=True)
class BrowserNodeConfig:
    action: BrowserAction
    output_key: str = "browser_output"

    # navigate
    url: str | None = None
    url_key: str | None = None

    # click
    selector: str | None = None
    som_index: int | None = None

    # type
    text: str | None = None
    text_key: str | None = None


class BrowserNode(BaseNode):
    """Browser node that executes a single action against a shared session."""

    def __init__(
        self,
        node_id: str,
        *,
        run_id: str,
        session_manager: BrowserSessionManager,
        session_factory: Callable[[], BrowserSession],
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="browser")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        self._run_id = run_id
        self._session_manager = session_manager
        self._session_factory = session_factory
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = self._parse_config(self._config)
        session = self._session_manager.get_or_create(self._run_id, self._session_factory)

        page = session.context
        # Basic runtime check: tests use fakes, Playwright will provide a Page.
        if not hasattr(page, "goto") or not hasattr(page, "click"):
            raise ValueError("BrowserSession.context must be page-like (goto/click/fill)")

        page_like: BrowserPageLike = page  # type: ignore[assignment]

        if cfg.action == "navigate":
            url = self._resolve_url(cfg, state)
            result = navigate(page_like, url=url)
        elif cfg.action == "click":
            selector = resolve_selector(state=state, selector=cfg.selector, som_index=cfg.som_index)
            result = click(page_like, selector=selector)
        elif cfg.action == "type":
            selector = resolve_selector(state=state, selector=cfg.selector, som_index=cfg.som_index)
            text = self._resolve_text(cfg, state)
            result = type_text(page_like, selector=selector, text=text)
        else:
            raise ValueError("Unsupported browser action")

        return {cfg.output_key: _result_to_dict(result)}

    @staticmethod
    def _parse_config(raw: dict[str, Any]) -> BrowserNodeConfig:
        action = raw.get("action")
        if action not in {"navigate", "click", "type"}:
            raise ValueError("BrowserNode config.action must be one of: navigate, click, type")

        output_key = raw.get("output_key", "browser_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("BrowserNode config.output_key must be a non-empty string")

        return BrowserNodeConfig(
            action=action,
            output_key=output_key,
            url=raw.get("url"),
            url_key=raw.get("url_key"),
            selector=raw.get("selector"),
            som_index=raw.get("som_index"),
            text=raw.get("text"),
            text_key=raw.get("text_key"),
        )

    @staticmethod
    def _resolve_url(cfg: BrowserNodeConfig, state: dict[str, Any]) -> str:
        if cfg.url is not None:
            if not isinstance(cfg.url, str) or not cfg.url.strip():
                raise ValueError("BrowserNode config.url must be a non-empty string")
            return cfg.url

        if cfg.url_key is None:
            raise ValueError("BrowserNode navigate requires config.url or config.url_key")
        if not isinstance(cfg.url_key, str) or not cfg.url_key:
            raise ValueError("BrowserNode config.url_key must be a non-empty string")

        value = state.get(cfg.url_key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"BrowserNode state[{cfg.url_key!r}] must be a non-empty string")
        return value

    @staticmethod
    def _resolve_text(cfg: BrowserNodeConfig, state: dict[str, Any]) -> str:
        if cfg.text is not None:
            if not isinstance(cfg.text, str):
                raise ValueError("BrowserNode config.text must be a string")
            return cfg.text

        if cfg.text_key is None:
            raise ValueError("BrowserNode type requires config.text or config.text_key")
        if not isinstance(cfg.text_key, str) or not cfg.text_key:
            raise ValueError("BrowserNode config.text_key must be a non-empty string")

        value = state.get(cfg.text_key)
        if not isinstance(value, str):
            raise ValueError(f"BrowserNode state[{cfg.text_key!r}] must be a string")
        return value


def _result_to_dict(result: BrowserActionResult) -> dict[str, Any]:
    return {"action": result.action, "ok": result.ok, "details": dict(result.details)}
