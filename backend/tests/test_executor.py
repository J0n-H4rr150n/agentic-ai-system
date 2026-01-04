import asyncio

import pytest

from backend.nodes.base import BaseNode
from backend.runner.executor import AsyncExecutor
from backend.runner.graph_parser import ExecutionPlan
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer


class RecordingNode(BaseNode):
    def __init__(self, node_id: str, output: dict[str, object]) -> None:
        super().__init__(node_id=node_id, node_type="recording")
        self._output = output
        self.seen_states: list[dict[str, object]] = []

    async def execute(self, state: dict[str, object]) -> dict[str, object]:
        # record a snapshot of the incoming state
        self.seen_states.append(dict(state))
        # yield once to allow concurrency in tests
        await asyncio.sleep(0)
        return dict(self._output)


def test_async_executor_runs_parallel_ready_nodes_and_merges_state_deterministically() -> None:
    # Graph:
    #   a -> b
    #   a -> c
    #   b -> d
    #   c -> d
    plan = ExecutionPlan(
        node_ids=["a", "b", "c", "d"],
        outgoing={"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []},
        incoming={"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]},
    )

    nodes: dict[str, BaseNode] = {
        "a": RecordingNode("a", output={"a": 1}),
        "b": RecordingNode("b", output={"b": 2}),
        "c": RecordingNode("c", output={"c": 3}),
        "d": RecordingNode("d", output={"d": 4}),
    }

    executor = AsyncExecutor()
    tracer = StepTracer()
    final_state = asyncio.run(executor.run(plan, nodes, state=StateContainer.from_mapping({"seed": True}), tracer=tracer))

    assert final_state.to_dict() == {"seed": True, "a": 1, "b": 2, "c": 3, "d": 4}

    # b and c should both see state after a merged, but not require each other.
    assert nodes["b"].seen_states == [{"seed": True, "a": 1}]
    assert nodes["c"].seen_states == [{"seed": True, "a": 1}]

    # d should see the merged results from a, b, and c.
    assert nodes["d"].seen_states == [{"seed": True, "a": 1, "b": 2, "c": 3}]

    steps = tracer.steps()
    assert [s.node_id for s in steps] == ["a", "b", "c", "d"]
    assert [s.status for s in steps] == ["ok", "ok", "ok", "ok"]

    # a sees initial state
    assert steps[0].input == {"seed": True}
    assert steps[0].output == {"a": 1}

    # b and c see state after a merged (batch snapshot)
    assert steps[1].input == {"seed": True, "a": 1}
    assert steps[2].input == {"seed": True, "a": 1}

    # d sees state after b and c merged
    assert steps[3].input == {"seed": True, "a": 1, "b": 2, "c": 3}

    for step in steps:
        assert isinstance(step.duration_ms, int)
        assert step.duration_ms >= 0


def test_async_executor_rejects_missing_nodes() -> None:
    plan = ExecutionPlan(node_ids=["a"], outgoing={"a": []}, incoming={"a": []})
    executor = AsyncExecutor()

    with pytest.raises(ValueError, match="Missing node implementations"):
        asyncio.run(executor.run(plan, nodes={}))
