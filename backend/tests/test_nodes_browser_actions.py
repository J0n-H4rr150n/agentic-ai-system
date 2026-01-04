import pytest

from backend.nodes.browser.actions import click, navigate, resolve_selector, type_text


class FakePage:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def goto(self, url: str):  # noqa: ANN201
        self.calls.append(("goto", url))

    def click(self, selector: str):  # noqa: ANN201
        self.calls.append(("click", selector))

    def fill(self, selector: str, text: str):  # noqa: ANN201
        self.calls.append(("fill", selector, text))


def test_resolve_selector_prefers_selector() -> None:
    sel = resolve_selector(state={}, selector="#x", som_index=None)
    assert sel == "#x"


def test_resolve_selector_can_use_som_index_from_state() -> None:
    sel = resolve_selector(state={"som_index_to_selector": {1: "#btn"}}, selector=None, som_index=1)
    assert sel == "#btn"


def test_resolve_selector_raises_if_missing_mapping() -> None:
    with pytest.raises(ValueError, match="som_index_to_selector"):
        resolve_selector(state={}, selector=None, som_index=1)


def test_actions_call_page_methods() -> None:
    page = FakePage()

    r1 = navigate(page, url="https://example.com")
    r2 = click(page, selector="#btn")
    r3 = type_text(page, selector="#q", text="hi")

    assert [c[0] for c in page.calls] == ["goto", "click", "fill"]
    assert r1.ok and r2.ok and r3.ok
