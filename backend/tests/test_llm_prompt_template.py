import pytest

from backend.nodes.llm.prompt_template import render_prompt_template


def test_render_prompt_template_replaces_placeholders() -> None:
    out = render_prompt_template("Hello {{name}}", {"name": "Ada"})
    assert out == "Hello Ada"


def test_render_prompt_template_supports_dotted_paths() -> None:
    out = render_prompt_template("URL={{browser.url}}", {"browser": {"url": "http://x"}})
    assert out == "URL=http://x"


def test_render_prompt_template_missing_value_becomes_empty() -> None:
    out = render_prompt_template("X={{missing}}", {})
    assert out == "X="


def test_render_prompt_template_rejects_non_string_template() -> None:
    with pytest.raises(TypeError):
        render_prompt_template(123, {})  # type: ignore[arg-type]
