import asyncio
import pytest

from backend.nodes.code_executor import CodeExecutorNode
from backend.nodes.base import NodeExecutionError


def test_code_executor_writes_default_output_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "1 + 2"})
    out = asyncio.run(node.execute({}))
    assert out == {"code_output": 3}


def test_code_executor_can_read_state_via_subscript() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state['a'] * 2"})
    out = asyncio.run(node.execute({"a": 5}))
    assert out == {"code_output": 10}


def test_code_executor_respects_output_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "10", "output_key": "x"})
    out = asyncio.run(node.execute({}))
    assert out == {"x": 10}


def test_code_executor_rejects_calls() -> None:
    node = CodeExecutorNode("n1", config={"expression": "len(state)"})
    with pytest.raises(NodeExecutionError, match="Unsupported expression syntax"):
        asyncio.run(node.execute({"a": 1}))


def test_code_executor_rejects_attribute_access() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state.__class__"})
    with pytest.raises(NodeExecutionError, match="Unsupported expression syntax"):
        asyncio.run(node.execute({"a": 1}))


def test_code_executor_reports_missing_state_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state['missing']"})
    with pytest.raises(NodeExecutionError, match="Missing state key"):
        asyncio.run(node.execute({}))
