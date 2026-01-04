"""Browser actions.

These helpers are written against lightweight protocols so we can unit test
without requiring Playwright or browser binaries.

Supported actions:
- navigate (goto URL)
- click (CSS selector or SoM index resolved from state)
- type (fill/typing into an input)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class BrowserPageLike(Protocol):
    def goto(self, url: str) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def click(self, selector: str) -> Any:  # noqa: ANN401
        raise NotImplementedError

    def fill(self, selector: str, text: str) -> Any:  # noqa: ANN401
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class BrowserActionResult:
    action: str
    ok: bool
    details: dict[str, Any]


def resolve_selector(*, state: dict[str, Any], selector: str | None, som_index: int | None) -> str:
    """Resolve a selector from either an explicit selector or a SoM index.

    SoM resolution expects a mapping in state under `som_index_to_selector`:
        state["som_index_to_selector"] = {1: "#submit", 2: "a.login"}
    """

    if selector is not None:
        if not isinstance(selector, str) or not selector.strip():
            raise ValueError("selector must be a non-empty string")
        return selector

    if som_index is None:
        raise ValueError("Either selector or som_index is required")

    if not isinstance(som_index, int) or som_index <= 0:
        raise ValueError("som_index must be a positive int")

    mapping = state.get("som_index_to_selector")
    if not isinstance(mapping, dict):
        raise ValueError("state['som_index_to_selector'] must be a dict")

    resolved = mapping.get(som_index)
    if not isinstance(resolved, str) or not resolved.strip():
        raise ValueError(f"No selector found for som_index={som_index}")

    return resolved


def navigate(page: BrowserPageLike, *, url: str) -> BrowserActionResult:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")
    page.goto(url)
    return BrowserActionResult(action="navigate", ok=True, details={"url": url})


def click(page: BrowserPageLike, *, selector: str) -> BrowserActionResult:
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("selector must be a non-empty string")
    page.click(selector)
    return BrowserActionResult(action="click", ok=True, details={"selector": selector})


def type_text(page: BrowserPageLike, *, selector: str, text: str) -> BrowserActionResult:
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("selector must be a non-empty string")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    page.fill(selector, text)
    return BrowserActionResult(action="type", ok=True, details={"selector": selector, "text": text})
