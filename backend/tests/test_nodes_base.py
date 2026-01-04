import asyncio

import pytest

from backend.nodes.base import BaseNode
from backend.nodes.mock import MockNode


def test_mock_node_executes_and_records_call() -> None:
    node = MockNode("n1", output={"value": 123})
    out = asyncio.run(node.execute({"k": "v"}))

    assert out == {"value": 123}
    assert node.calls == [{"state": {"k": "v"}}]


def test_base_node_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseNode("n1", "t")
