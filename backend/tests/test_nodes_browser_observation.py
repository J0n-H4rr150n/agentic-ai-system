from __future__ import annotations

import base64

import pytest

from backend.nodes.browser.observation import build_html_cleaned, build_observation


class FakePage:
    def __init__(self) -> None:
        self._network_log = [
            {"url": "https://example.test/api", "method": "GET", "response": "ok"},
        ]

    def screenshot(self) -> bytes:
        return b"png-bytes"

    def screenshot_som(self) -> bytes:
        return b"png-som-bytes"

    def content(self) -> str:
        return "<html><!-- secret: 123 --><script>alert(1)</script><body>Hi</body></html>"

    def get_network_log(self):
        return list(self._network_log)


def test_build_observation_visual_includes_screenshot_and_som() -> None:
    obs = build_observation(mode="visual", page=FakePage()).to_dict()
    assert obs["screenshot"] == base64.b64encode(b"png-bytes").decode("ascii")
    assert obs["screenshot_som"] == base64.b64encode(b"png-som-bytes").decode("ascii")
    assert "html_cleaned" not in obs
    assert "network_log" not in obs


def test_build_observation_source_inspector_includes_cleaned_html() -> None:
    obs = build_observation(mode="source_inspector", page=FakePage()).to_dict()
    assert "EXTRACTED_COMMENTS" in obs["html_cleaned"]
    assert "secret: 123" in obs["html_cleaned"]
    assert "<script" not in obs["html_cleaned"].lower()
    assert "network_log" not in obs


def test_build_observation_traffic_analyst_includes_network_log() -> None:
    obs = build_observation(mode="traffic_analyst", page=FakePage()).to_dict()
    assert obs["network_log"] == [{"url": "https://example.test/api", "method": "GET", "response": "ok"}]
    assert "screenshot" not in obs
    assert "html_cleaned" not in obs


def test_build_observation_full_includes_everything() -> None:
    obs = build_observation(mode="full", page=FakePage()).to_dict()
    assert "screenshot" in obs
    assert "screenshot_som" in obs
    assert "html_cleaned" in obs
    assert "network_log" in obs


def test_build_html_cleaned_rejects_non_string() -> None:
    with pytest.raises(ValueError):
        build_html_cleaned(None)  # type: ignore[arg-type]
