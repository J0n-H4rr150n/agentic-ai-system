import asyncio

from backend.nodes.llm.vertex import VertexAILLMClient, VertexAISettings


class _FakeUsage:
    def __init__(self, prompt_token_count: int, candidates_token_count: int) -> None:
        self.prompt_token_count = prompt_token_count
        self.candidates_token_count = candidates_token_count


class _FakeResponse:
    def __init__(self, text: str, usage: _FakeUsage | None = None) -> None:
        self.text = text
        self.usage_metadata = usage


class _FakeModel:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate_content(self, prompt: str, generation_config=None):  # noqa: ANN001
        self.calls.append({"prompt": prompt, "generation_config": generation_config})
        usage = _FakeUsage(prompt_token_count=3, candidates_token_count=5)
        return _FakeResponse(text='{"ok":true}', usage=usage)


def test_vertex_client_passes_json_mime_type_and_extracts_usage() -> None:
    fake_model = _FakeModel()
    init_calls: list[str] = []

    def _init() -> None:
        init_calls.append("init")

    client = VertexAILLMClient(
        settings=VertexAISettings(project="p", location="l"),
        init_fn=_init,
        model_factory=lambda _: fake_model,
    )

    resp = asyncio.run(
        client.complete(model="gemini-2.5-flash", prompt="hi", json_mode=True, temperature=0.2, max_output_tokens=10)
    )

    assert init_calls == ["init"]
    assert resp.json == {"ok": True}
    assert resp.usage is not None
    assert resp.usage.input_tokens == 3
    assert resp.usage.output_tokens == 5

    assert fake_model.calls == [
        {
            "prompt": "hi",
            "generation_config": {
                "temperature": 0.2,
                "max_output_tokens": 10,
                "response_mime_type": "application/json",
            },
        }
    ]


def test_vertex_client_initializes_only_once() -> None:
    fake_model = _FakeModel()
    init_calls: list[str] = []

    def _init() -> None:
        init_calls.append("init")

    client = VertexAILLMClient(
        settings=VertexAISettings(project="p", location="l"),
        init_fn=_init,
        model_factory=lambda _: fake_model,
    )

    asyncio.run(client.complete(model="m", prompt="p", json_mode=False))
    asyncio.run(client.complete(model="m", prompt="p", json_mode=False))

    assert init_calls == ["init"]
