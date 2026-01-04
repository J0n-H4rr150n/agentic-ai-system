import pytest

from backend.runner.dependency import topological_sort
from backend.runner.graph_parser import ExecutionPlan


def test_topological_sort_orders_simple_dag() -> None:
    plan = ExecutionPlan(
        node_ids=["a", "b", "c"],
        outgoing={"a": ["b", "c"], "b": ["c"], "c": []},
        incoming={"a": [], "b": ["a"], "c": ["a", "b"]},
    )

    order = topological_sort(plan)
    assert order == ["a", "b", "c"]


def test_topological_sort_detects_cycle() -> None:
    plan = ExecutionPlan(
        node_ids=["a", "b"],
        outgoing={"a": ["b"], "b": ["a"]},
        incoming={"a": ["b"], "b": ["a"]},
    )

    with pytest.raises(ValueError, match="cycle"):
        topological_sort(plan)
