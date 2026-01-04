"""Router node.

This node evaluates a list of conditions against the run state and selects a
named output route.

Note: The current runner executes all nodes in a DAG and does not yet support
conditional edge skipping based on selected routes. This node therefore outputs
its selection for downstream nodes (and future runner logic) to consume.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from backend.nodes.base import BaseNode


ConditionOp = Literal["equals", "contains", "regex", "greater_than", "less_than"]


@dataclass(frozen=True, slots=True)
class RouterCondition:
    var: str
    op: ConditionOp
    value: Any
    output: str


@dataclass(frozen=True, slots=True)
class RouterNodeConfig:
    output_key: str = "router_output"
    default_output: str = "default"
    conditions: list[RouterCondition] = None  # type: ignore[assignment]


class RouterNode(BaseNode):
    """Control node that selects a route based on state."""

    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="router")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = _parse_config(self._config)

        selected, matched = select_route(state=state, conditions=cfg.conditions, default_output=cfg.default_output)

        return {
            cfg.output_key: {
                "selected_port": selected,
                "matched": matched,
            }
        }


NODE_TYPE = "router"
NODE_CLASS = RouterNode


def select_route(
    *,
    state: dict[str, Any],
    conditions: list[RouterCondition],
    default_output: str,
) -> tuple[str, bool]:
    """Select the first matching route; otherwise return the default."""

    for condition in conditions:
        if evaluate_condition(state=state, condition=condition):
            return condition.output, True

    return default_output, False


def evaluate_condition(*, state: dict[str, Any], condition: RouterCondition) -> bool:
    value = get_state_value(state=state, path=condition.var)

    if condition.op == "equals":
        return value == condition.value

    if condition.op == "contains":
        if value is None:
            return False
        needle = condition.value
        if isinstance(value, str):
            if not isinstance(needle, str):
                return False
            return needle in value
        if isinstance(value, (list, tuple, set)):
            return needle in value
        return False

    if condition.op == "regex":
        if value is None:
            return False
        if not isinstance(value, str):
            return False
        if not isinstance(condition.value, str) or not condition.value:
            return False
        return re.search(condition.value, value) is not None

    if condition.op == "greater_than":
        return _compare_numbers(value, condition.value, op=">")

    if condition.op == "less_than":
        return _compare_numbers(value, condition.value, op="<")

    raise ValueError("Unsupported condition op")


def get_state_value(*, state: dict[str, Any], path: str) -> Any:
    """Get a value from state, supporting dotted paths into nested dicts."""

    if not isinstance(path, str) or not path:
        raise ValueError("var must be a non-empty string")

    current: Any = state
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _compare_numbers(left: Any, right: Any, *, op: Literal[">", "<"]) -> bool:
    if not isinstance(left, (int, float)) or isinstance(left, bool):
        return False
    if not isinstance(right, (int, float)) or isinstance(right, bool):
        return False

    if op == ">":
        return float(left) > float(right)
    return float(left) < float(right)


def _parse_config(raw: dict[str, Any]) -> RouterNodeConfig:
    output_key = raw.get("output_key", "router_output")
    if not isinstance(output_key, str) or not output_key:
        raise ValueError("RouterNode config.output_key must be a non-empty string")

    default_output = raw.get("default_output", "default")
    if not isinstance(default_output, str) or not default_output:
        raise ValueError("RouterNode config.default_output must be a non-empty string")

    conditions_raw = raw.get("conditions")
    if conditions_raw is None:
        conditions_raw = []
    if not isinstance(conditions_raw, list):
        raise ValueError("RouterNode config.conditions must be a list")

    conditions: list[RouterCondition] = []
    for idx, item in enumerate(conditions_raw):
        if not isinstance(item, dict):
            raise ValueError("RouterNode config.conditions items must be dicts")

        var = item.get("var")
        op = item.get("op")
        output = item.get("output")

        if not isinstance(var, str) or not var:
            raise ValueError(f"RouterNode condition[{idx}] var must be a non-empty string")
        if op not in {"equals", "contains", "regex", "greater_than", "less_than"}:
            raise ValueError(
                f"RouterNode condition[{idx}] op must be one of: equals, contains, regex, greater_than, less_than"
            )
        if not isinstance(output, str) or not output:
            raise ValueError(f"RouterNode condition[{idx}] output must be a non-empty string")

        value = item.get("value")
        if op == "regex":
            if not isinstance(value, str) or not value:
                raise ValueError(f"RouterNode condition[{idx}] value must be a non-empty string for regex")
            try:
                re.compile(value)
            except re.error as exc:  # noqa: BLE001
                raise ValueError(f"RouterNode condition[{idx}] invalid regex: {exc}") from exc

        conditions.append(RouterCondition(var=var, op=op, value=value, output=output))

    return RouterNodeConfig(output_key=output_key, default_output=default_output, conditions=conditions)
