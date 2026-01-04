import pytest

from backend.nodes.code_executor import CodeExecutorNode
from backend.nodes.base import NodeExecutionError


@pytest.mark.asyncio
async def test_code_executor_writes_default_output_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "1 + 2"})
    out = await node.execute({})
    assert out == {"code_output": 3}


@pytest.mark.asyncio
async def test_code_executor_can_read_state_via_subscript() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state['a'] * 2"})
    out = await node.execute({"a": 5})
    assert out == {"code_output": 10}


@pytest.mark.asyncio
async def test_code_executor_respects_output_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "10", "output_key": "x"})
    out = await node.execute({})
    assert out == {"x": 10}


@pytest.mark.asyncio
async def test_code_executor_rejects_calls() -> None:
    node = CodeExecutorNode("n1", config={"expression": "len(state)"})
    with pytest.raises(NodeExecutionError, match="Unsupported expression syntax"):
        await node.execute({"a": 1})


@pytest.mark.asyncio
async def test_code_executor_rejects_attribute_access() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state.__class__"})
    with pytest.raises(NodeExecutionError, match="Unsupported expression syntax"):
        await node.execute({"a": 1})


@pytest.mark.asyncio
async def test_code_executor_reports_missing_state_key() -> None:
    node = CodeExecutorNode("n1", config={"expression": "state['missing']"})
    with pytest.raises(NodeExecutionError, match="Missing state key"):
        await node.execute({})
