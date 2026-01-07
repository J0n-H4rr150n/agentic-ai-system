import asyncio

import pytest

from backend.nodes.control.input import InputNode


def test_input_node_stores_value_under_output_key() -> None:
    node = InputNode("n1", config={"value": "http://example.test", "output_key": "target_url"})
    out = asyncio.run(node.execute({}))
    assert out == {"target_url": "http://example.test"}


def test_input_node_default_output_key() -> None:
    node = InputNode("n1", config={"value": "x"})
    out = asyncio.run(node.execute({}))
    assert out == {"input_value": "x"}


def test_input_node_rejects_non_string_value() -> None:
    node = InputNode("n1", config={"value": 123, "output_key": "k"})
    with pytest.raises(ValueError, match="config.value"):
        asyncio.run(node.execute({}))


def test_input_node_requires_non_empty_output_key() -> None:
    node = InputNode("n1", config={"value": "x", "output_key": ""})
    with pytest.raises(ValueError, match="config.output_key"):
        asyncio.run(node.execute({}))
