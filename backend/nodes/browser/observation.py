"""Browser observations.

Observation modes determine what data the browser node captures after performing
an action.

Modes (from `.implementation/F00003_core_node_library.md`):
- visual: screenshot + screenshot_som
- source_inspector: html_cleaned with comments extracted
- traffic_analyst: network_log array
- full: everything

This module stays Playwright-optional by relying on small protocols.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol


ObservationMode = Literal["visual", "source_inspector", "traffic_analyst", "full"]


class BrowserObservationPageLike(Protocol):
    def screenshot(self) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def content(self) -> Any:  # noqa: ANN401
        raise NotImplementedError


class BrowserNetworkLogSource(Protocol):
    def get_network_log(self) -> Any:  # noqa: ANN401
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class BrowserObservation:
    screenshot: str | None = None
    screenshot_som: str | None = None
    html_source: str | None = None
    html_cleaned: str | None = None
    network_log: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.screenshot is not None:
            out["screenshot"] = self.screenshot
        if self.screenshot_som is not None:
            out["screenshot_som"] = self.screenshot_som
        if self.html_source is not None:
            out["html_source"] = self.html_source
        if self.html_cleaned is not None:
            out["html_cleaned"] = self.html_cleaned
        if self.network_log is not None:
            out["network_log"] = self.network_log
        return out


def build_observation(*, mode: ObservationMode, page: Any) -> BrowserObservation:
    """Build an observation payload for the requested mode."""

    screenshot_b64: str | None = None
    screenshot_som_b64: str | None = None
    html_source: str | None = None
    html_cleaned: str | None = None
    network_log: list[dict[str, Any]] | None = None

    if mode in {"visual", "full"}:
        screenshot_b64 = _try_get_screenshot_base64(page)
        screenshot_som_b64 = _try_get_screenshot_som_base64(page, fallback=screenshot_b64)

    if mode in {"source_inspector", "full"}:
        html_source = _try_get_html_source(page)
        if html_source is not None:
            html_cleaned = build_html_cleaned(html_source)

    if mode in {"traffic_analyst", "full"}:
        network_log = _try_get_network_log(page)

    return BrowserObservation(
        screenshot=screenshot_b64,
        screenshot_som=screenshot_som_b64,
        html_source=html_source,
        html_cleaned=html_cleaned,
        network_log=network_log,
    )


def build_html_cleaned(html_source: str) -> str:
    """Return a text payload with extracted comments and scripts removed.

    The output is a single string (for easy downstream prompting) with this shape:

        EXTRACTED_COMMENTS:\n- comment...\n\nCLEAN_HTML:\n<html>...</html>

    This matches the spec requirement "html_cleaned with comments extracted" while
    keeping the payload minimal.
    """

    if not isinstance(html_source, str):
        raise ValueError("html_source must be a string")

    comments = _extract_html_comments(html_source)
    without_comments = _strip_html_comments(html_source)
    without_scripts = _strip_script_tags(without_comments)

    comments_block = "\n".join(f"- {c}" for c in comments) if comments else "(none)"
    return f"EXTRACTED_COMMENTS:\n{comments_block}\n\nCLEAN_HTML:\n{without_scripts}".strip()


_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.IGNORECASE | re.DOTALL)


def _extract_html_comments(html_source: str) -> list[str]:
    return [m.strip() for m in _COMMENT_RE.findall(html_source) if m.strip()]


def _strip_html_comments(html_source: str) -> str:
    return _COMMENT_RE.sub("", html_source)


def _strip_script_tags(html_source: str) -> str:
    return _SCRIPT_RE.sub("", html_source)


def _try_get_html_source(page: Any) -> str | None:
    content = getattr(page, "content", None)
    if not callable(content):
        return None

    value = content()
    if isinstance(value, str):
        return value
    return None


def _try_get_screenshot_base64(page: Any) -> str | None:
    screenshot = getattr(page, "screenshot", None)
    if not callable(screenshot):
        return None

    value = screenshot()
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, str) and value.strip():
        # Allows callers/fakes to return already-encoded screenshot payloads.
        return value
    return None


def _try_get_screenshot_som_base64(page: Any, *, fallback: str | None) -> str | None:
    screenshot_som = getattr(page, "screenshot_som", None)
    if callable(screenshot_som):
        value = screenshot_som()
        if isinstance(value, bytes):
            return base64.b64encode(value).decode("ascii")
        if isinstance(value, str) and value.strip():
            return value

    return fallback


def _try_get_network_log(page: Any) -> list[dict[str, Any]]:
    # Prefer an explicit getter (easy to fake + avoids grabbing internal state).
    get_network_log = getattr(page, "get_network_log", None)
    if callable(get_network_log):
        value = get_network_log()
        return _coerce_network_log(value)

    # Fallback: treat a `network_log` attribute as the payload.
    value = getattr(page, "network_log", None)
    return _coerce_network_log(value)


def _coerce_network_log(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("network_log must be a list")

    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("network_log items must be dicts")
        out.append(dict(item))
    return out
