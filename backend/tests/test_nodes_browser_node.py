import asyncio

import pytest

from backend.nodes.browser.node import BrowserNode
from backend.nodes.browser.session import BrowserSession, BrowserSessionManager


class FakePage:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def goto(self, url: str):  # noqa: ANN201
        self.calls.append(("goto", url))

    def click(self, selector: str):  # noqa: ANN201
        self.calls.append(("click", selector))

    def fill(self, selector: str, text: str):  # noqa: ANN201
        self.calls.append(("fill", selector, text))

    def screenshot(self):  # noqa: ANN201
        self.calls.append(("screenshot",))
        return b"png-bytes"

    def screenshot_som(self):  # noqa: ANN201
        self.calls.append(("screenshot_som",))
        return b"png-som-bytes"

    def content(self):  # noqa: ANN201
        self.calls.append(("content",))
        return "<html><!-- note --><body>Hi</body></html>"

    def get_network_log(self):  # noqa: ANN201
        self.calls.append(("get_network_log",))
        return [{"url": "https://example.test/api", "method": "GET", "response": "ok"}]


def test_browser_node_navigate_uses_config_url() -> None:
    mgr = BrowserSessionManager()
    page = FakePage()

    node = BrowserNode(
        "b1",
        run_id="run-1",
        session_manager=mgr,
        session_factory=lambda: BrowserSession(context=page),
        config={"action": "navigate", "url": "https://example.com"},
    )

    out = asyncio.run(node.execute({}))
    assert out["browser_output"]["action"] == "navigate"
    assert page.calls == [("goto", "https://example.com")]


def test_browser_node_click_resolves_som_index() -> None:
    mgr = BrowserSessionManager()
    page = FakePage()

    node = BrowserNode(
        "b1",
        run_id="run-1",
        session_manager=mgr,
        session_factory=lambda: BrowserSession(context=page),
        config={"action": "click", "som_index": 1},
    )

    state = {"som_index_to_selector": {1: "#btn"}}
    out = asyncio.run(node.execute(state))
    assert out["browser_output"]["details"]["selector"] == "#btn"
    assert page.calls == [("click", "#btn")]


def test_browser_node_type_uses_text_key() -> None:
    mgr = BrowserSessionManager()
    page = FakePage()

    node = BrowserNode(
        "b1",
        run_id="run-1",
        session_manager=mgr,
        session_factory=lambda: BrowserSession(context=page),
        config={"action": "type", "selector": "#q", "text_key": "query"},
    )

    out = asyncio.run(node.execute({"query": "hello"}))
    assert out["browser_output"]["details"]["text"] == "hello"
    assert page.calls == [("fill", "#q", "hello")]


def test_browser_node_rejects_missing_action() -> None:
    mgr = BrowserSessionManager()
    page = FakePage()

    node = BrowserNode(
        "b1",
        run_id="run-1",
        session_manager=mgr,
        session_factory=lambda: BrowserSession(context=page),
        config={},
    )

    with pytest.raises(ValueError, match="config.action"):
        asyncio.run(node.execute({}))


def test_browser_node_observation_mode_full_merges_into_output() -> None:
    mgr = BrowserSessionManager()
    page = FakePage()

    node = BrowserNode(
        "b1",
        run_id="run-1",
        session_manager=mgr,
        session_factory=lambda: BrowserSession(context=page),
        config={"action": "navigate", "url": "https://example.com", "observation_mode": "full"},
    )

    out = asyncio.run(node.execute({}))
    payload = out["browser_output"]

    assert payload["action"] == "navigate"
    assert payload["screenshot"]
    assert payload["screenshot_som"]
    assert "EXTRACTED_COMMENTS" in payload["html_cleaned"]
    assert payload["network_log"] == [{"url": "https://example.test/api", "method": "GET", "response": "ok"}]
