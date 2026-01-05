import asyncio

import pytest

from backend.nodes.control.end import EndNode
from backend.nodes.control.parallel_gate import ParallelGateNode
from backend.nodes.control.router import RouterNode
from backend.nodes.control.start import StartNode


def test_start_node_returns_empty_without_initial_state() -> None:
    node = StartNode("s1", config={})
    out = asyncio.run(node.execute({"existing": 1}))
    assert out == {}


def test_start_node_returns_initial_state_mapping() -> None:
    node = StartNode("s1", config={"initial_state": {"a": 1, "b": "x"}})
    out = asyncio.run(node.execute({}))
    assert out == {"a": 1, "b": "x"}


def test_start_node_rejects_non_dict_initial_state() -> None:
    node = StartNode("s1", config={"initial_state": [1, 2, 3]})
    with pytest.raises(ValueError, match="initial_state must be a dict"):
        asyncio.run(node.execute({}))


def test_end_node_returns_result_snapshot_default_key() -> None:
    node = EndNode("e1", config={})
    out = asyncio.run(node.execute({"x": 1, "y": "z"}))
    assert out == {"result": {"x": 1, "y": "z"}}


def test_end_node_excludes_result_key_from_snapshot() -> None:
    node = EndNode("e1", config={})
    out = asyncio.run(node.execute({"result": {"old": True}, "x": 1}))
    assert out == {"result": {"x": 1}}


def test_end_node_can_limit_included_keys() -> None:
    node = EndNode("e1", config={"include_keys": ["a", "c"]})
    out = asyncio.run(node.execute({"a": 1, "b": 2, "c": 3}))
    assert out == {"result": {"a": 1, "c": 3}}


def test_end_node_rejects_bad_result_key() -> None:
    node = EndNode("e1", config={"result_key": ""})
    with pytest.raises(ValueError, match="result_key"):
        asyncio.run(node.execute({"x": 1}))


def test_router_node_selects_first_matching_condition() -> None:
    node = RouterNode(
        "r1",
        config={
            "default_output": "fallback",
            "conditions": [
                {"var": "score", "op": "greater_than", "value": 90, "output": "high"},
                {"var": "score", "op": "greater_than", "value": 50, "output": "medium"},
            ],
        },
    )

    out = asyncio.run(node.execute({"score": 95}))
    assert out["router_output"] == {"selected_port": "high", "matched": True}


def test_router_node_uses_default_when_no_conditions_match() -> None:
    node = RouterNode(
        "r1",
        config={
            "default_output": "fallback",
            "conditions": [
                {"var": "status", "op": "equals", "value": "ok", "output": "ok_port"},
            ],
        },
    )

    out = asyncio.run(node.execute({"status": "nope"}))
    assert out["router_output"] == {"selected_port": "fallback", "matched": False}


def test_router_node_supports_contains_and_regex() -> None:
    node = RouterNode(
        "r1",
        config={
            "conditions": [
                {"var": "msg", "op": "contains", "value": "token", "output": "contains"},
                {"var": "msg", "op": "regex", "value": "t[0-9]+n", "output": "regex"},
            ],
        },
    )

    out = asyncio.run(node.execute({"msg": "found token"}))
    assert out["router_output"]["selected_port"] == "contains"


def test_router_node_supports_dotted_state_paths() -> None:
    node = RouterNode(
        "r1",
        config={
            "default_output": "fallback",
            "conditions": [
                {"var": "user.role", "op": "equals", "value": "admin", "output": "admin"},
            ],
        },
    )

    out = asyncio.run(node.execute({"user": {"role": "admin"}}))
    assert out["router_output"]["selected_port"] == "admin"


def test_router_node_rejects_invalid_regex() -> None:
    node = RouterNode(
        "r1",
        config={"conditions": [{"var": "x", "op": "regex", "value": "(", "output": "bad"}]},
    )
    with pytest.raises(ValueError, match="invalid regex"):
        asyncio.run(node.execute({"x": "hello"}))


def test_parallel_gate_join_outputs_default_key() -> None:
    node = ParallelGateNode("g1", config={"gate": "join"})
    out = asyncio.run(node.execute({"x": 1}))
    assert out == {"parallel_gate_output": {"gate": "join"}}


def test_parallel_gate_fork_requires_fanout() -> None:
    node = ParallelGateNode("g1", config={"gate": "fork"})
    with pytest.raises(ValueError, match="fanout"):
        asyncio.run(node.execute({}))


def test_parallel_gate_fork_accepts_fanout_and_outputs_it() -> None:
    node = ParallelGateNode("g1", config={"gate": "fork", "fanout": 2, "output_key": "pg"})
    out = asyncio.run(node.execute({}))
    assert out == {"pg": {"gate": "fork", "fanout": 2}}
