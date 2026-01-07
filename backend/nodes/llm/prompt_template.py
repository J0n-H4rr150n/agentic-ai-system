"""Prompt template rendering for LLM nodes.

Supports simple `{{path}}` substitutions using values from the run state.
Paths may be dotted (e.g., `browser_output.text`).

This module is pure and unit-testable.
"""

from __future__ import annotations

import json
import re
from typing import Any


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}")


def render_prompt_template(template: str, state: dict[str, Any]) -> str:
    """Render `template` by replacing `{{path}}` placeholders with state values."""

    if not isinstance(template, str):
        raise TypeError("template must be a string")
    if not isinstance(state, dict):
        raise TypeError("state must be a dict")

    def _replace(match: re.Match[str]) -> str:
        path = match.group(1)
        value = _get_state_value(state=state, path=path)
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:  # noqa: BLE001
            return str(value)

    return _PLACEHOLDER_RE.sub(_replace, template)


def _get_state_value(*, state: dict[str, Any], path: str) -> Any:
    if not isinstance(path, str) or not path:
        return None

    current: Any = state
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current
