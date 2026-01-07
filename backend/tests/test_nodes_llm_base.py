import asyncio

import pytest

from backend.nodes.llm.base import LLMCallNode, LLMResponse, LLMUsage


class FakeLLMClient:
    def __init__(self, response: LLMResponse) -> None:
        self._response = response
        self.calls: list[dict] = []

    async def complete(
        self,
        *,
        model: str,
        prompt: str,
        json_mode: bool,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> LLMResponse:
        self.calls.append(
            {
                "model": model,
                "prompt": prompt,
                "json_mode": json_mode,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
        )
        return self._response


def test_llm_call_node_uses_config_prompt_and_model() -> None:
    client = FakeLLMClient(LLMResponse(text="hi", usage=LLMUsage(input_tokens=1, output_tokens=2)))
    node = LLMCallNode("n1", client=client, config={"model": "gemini-2.5-flash", "prompt": "hello"})

    out = asyncio.run(node.execute({"ignored": True}))

    assert out["llm_output"]["model"] == "gemini-2.5-flash"
    assert out["llm_output"]["text"] == "hi"
    assert out["llm_output"]["json"] is None
    assert out["llm_output"]["usage"] == {"input_tokens": 1, "output_tokens": 2}
    assert isinstance(out["llm_output"]["trace"]["elapsed_time_ms"], int)
    assert out["llm_output"]["trace"]["input_tokens"] == 1
    assert out["llm_output"]["trace"]["output_tokens"] == 2
    assert client.calls == [{"model": "gemini-2.5-flash", "prompt": "hello", "json_mode": False, "temperature": None, "max_output_tokens": None}]


def test_llm_call_node_renders_prompt_templates() -> None:
    client = FakeLLMClient(LLMResponse(text="ok"))
    node = LLMCallNode("n1", client=client, config={"model": "m", "prompt": "Analyze {{url}}"})

    out = asyncio.run(node.execute({"url": "http://example.test"}))
    assert out["llm_output"]["text"] == "ok"
    assert client.calls[0]["prompt"] == "Analyze http://example.test"


def test_llm_call_node_supports_system_prompt_prefix() -> None:
    client = FakeLLMClient(LLMResponse(text="ok"))
    node = LLMCallNode(
        "n1",
        client=client,
        config={"model": "m", "system_prompt": "Be strict about JSON", "prompt": "Say hi"},
    )

    asyncio.run(node.execute({}))
    assert "System:" in client.calls[0]["prompt"]
    assert "Be strict about JSON" in client.calls[0]["prompt"]
    assert "User:" in client.calls[0]["prompt"]
    assert "Say hi" in client.calls[0]["prompt"]


def test_llm_call_node_can_read_prompt_from_state() -> None:
    client = FakeLLMClient(LLMResponse(text="ok"))
    node = LLMCallNode(
        "n1",
        client=client,
        config={"model": "gemini-2.5-pro", "prompt_key": "prompt"},
    )

    out = asyncio.run(node.execute({"prompt": "from_state"}))
    assert out["llm_output"]["text"] == "ok"
    assert client.calls[0]["prompt"] == "from_state"


def test_llm_call_node_json_mode_parses_text_when_json_missing() -> None:
    client = FakeLLMClient(LLMResponse(text='{"a":1}'))
    node = LLMCallNode("n1", client=client, config={"model": "m", "prompt": "p", "json_mode": True})

    out = asyncio.run(node.execute({}))
    assert out["llm_output"]["json"] == {"a": 1}


def test_llm_call_node_extracts_decision_fields_from_json() -> None:
    client = FakeLLMClient(LLMResponse(json={"llm_decision": "allow", "llm_reasoning": "ok", "llm_confidence": 0.7}))
    node = LLMCallNode("n1", client=client, config={"model": "m", "prompt": "p", "json_mode": True})

    out = asyncio.run(node.execute({}))
    trace = out["llm_output"]["trace"]
    assert trace["llm_decision"] == "allow"
    assert trace["llm_reasoning"] == "ok"
    assert trace["llm_confidence"] == 0.7


def test_llm_call_node_json_mode_raises_on_invalid_json_text() -> None:
    client = FakeLLMClient(LLMResponse(text="not-json"))
    node = LLMCallNode("n1", client=client, config={"model": "m", "prompt": "p", "json_mode": True})

    with pytest.raises(ValueError, match="expected JSON"):
        asyncio.run(node.execute({}))


def test_llm_call_node_requires_model() -> None:
    client = FakeLLMClient(LLMResponse(text="hi"))
    node = LLMCallNode("n1", client=client, config={"prompt": "hello"})

    with pytest.raises(ValueError, match="config.model"):
        asyncio.run(node.execute({}))


def test_llm_call_node_output_schema_forces_json_mode_and_extracts_fields() -> None:
    client = FakeLLMClient(LLMResponse(json={"confidence": 0.8, "action": "click"}))
    node = LLMCallNode(
        "n1",
        client=client,
        config={
            "model": "m",
            "prompt": "p",
            "json_mode": False,
            "output_schema": '{"confidence": "number", "action": "string"}',
        },
    )

    out = asyncio.run(node.execute({}))
    assert client.calls[0]["json_mode"] is True
    assert out["llm_confidence"] == 0.8
    assert out["llm_action"] == "click"


def test_llm_call_node_output_schema_rejects_missing_fields() -> None:
    client = FakeLLMClient(LLMResponse(json={"confidence": 0.8}))
    node = LLMCallNode(
        "n1",
        client=client,
        config={"model": "m", "prompt": "p", "output_schema": '{"confidence": "number", "action": "string"}'},
    )

    with pytest.raises(ValueError, match="missing required output_schema field"):
        asyncio.run(node.execute({}))
