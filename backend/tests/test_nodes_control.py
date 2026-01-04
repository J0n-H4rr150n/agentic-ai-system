import asyncio

import pytest

from backend.nodes.control.end import EndNode
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
