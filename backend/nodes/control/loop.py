"""Loop node.

Executes a saved workflow (subgraph) repeatedly as a single node.

Important runner constraint:
- The runner executes DAGs and does not support cyclic graphs. The loop is
  implemented *inside* this node by repeatedly executing a referenced workflow.

Config:
  workflow_id: Required workflow id to load.
  version: Optional integer version to load (defaults to latest).
  max_iterations: Optional int >= 1 (default: 10).
  break_key: Required dotted state path; when truthy after an iteration, stop.
  iteration_key: Optional state key written before each iteration (default:
    "loop_iteration"). Value is 1-based iteration number.
  output_key: Optional root state key to write loop summary (default:
    "loop_output").

Output:
  Returns the subgraph final state mapping merged with:
  - a reserved `__loop__` metadata mapping
  - `{output_key: {...}}` summary mapping
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.nodes.base import BaseNode
from backend.nodes.control.router import get_state_value
from backend.runner.dependency import topological_sort
from backend.runner.executor import AsyncExecutor
from backend.runner.graph_parser import parse_graph
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer
from backend.workflows.store import WorkflowStore


@dataclass(frozen=True, slots=True)
class LoopNodeConfig:
    workflow_id: str
    version: int | None
    max_iterations: int
    break_key: str
    iteration_key: str
    output_key: str


class LoopNode(BaseNode):
    def __init__(
        self,
        node_id: str,
        *,
        run_id: str,
        store: WorkflowStore,
        mode: str = "run",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="loop")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(store, WorkflowStore):
            raise ValueError("store must be a WorkflowStore")
        if mode not in {"run", "simulate", "test"}:
            raise ValueError("mode must be one of: run, simulate, test")

        self._run_id = run_id
        self._store = store
        self._mode = mode
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = _parse_config(self._config)

        try:
            _, selected = self._store.get(cfg.workflow_id, version=cfg.version)
        except KeyError as exc:
            raise ValueError(
                f"LoopNode could not load workflow_id={cfg.workflow_id!r} version={cfg.version!r}"
            ) from exc

        plan = parse_graph(selected.graph)
        topological_sort(plan)

        # Import locally to avoid circular imports (node_factory imports LoopNode).
        from backend.runner.node_factory import build_nodes_for_graph

        nodes = build_nodes_for_graph(run_id=self._run_id, graph_nodes=selected.graph.nodes, mode=self._mode)
        executor = AsyncExecutor()

        run_state = StateContainer.from_mapping(state)

        stopped_reason = "max_iterations"
        break_value: Any = None

        traces: list[list[dict[str, Any]]] = []

        for iteration in range(1, cfg.max_iterations + 1):
            run_state.update({cfg.iteration_key: iteration})

            tracer = StepTracer()
            run_state = await executor.run(plan, nodes, state=run_state, tracer=tracer)

            snapshot = run_state.to_dict()
            break_value = get_state_value(state=snapshot, path=cfg.break_key)

            traces.append([step.model_dump() for step in tracer.steps()])

            if break_value:
                stopped_reason = "break"
                break

        output = run_state.to_dict()
        output["__loop__"] = {
            "workflow_id": cfg.workflow_id,
            "version": selected.version,
            "iterations": len(traces),
            "stopped_reason": stopped_reason,
            "break_key": cfg.break_key,
            "break_value": break_value,
            "trace": traces,
        }
        output[cfg.output_key] = {
            "iterations": len(traces),
            "stopped_reason": stopped_reason,
            "break_key": cfg.break_key,
            "break_value": break_value,
        }
        return output


NODE_TYPE = "loop"
NODE_CLASS = LoopNode


def _parse_config(raw: dict[str, Any]) -> LoopNodeConfig:
    workflow_id = raw.get("workflow_id")
    if not isinstance(workflow_id, str) or not workflow_id:
        raise ValueError("LoopNode config.workflow_id must be a non-empty string")

    version = raw.get("version")
    if version is not None:
        if not isinstance(version, int) or version < 1:
            raise ValueError("LoopNode config.version must be an int >= 1 if provided")

    max_iterations = raw.get("max_iterations", 10)
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations < 1:
        raise ValueError("LoopNode config.max_iterations must be an int >= 1")
    if max_iterations > 1000:
        raise ValueError("LoopNode config.max_iterations must be <= 1000")

    break_key = raw.get("break_key")
    if not isinstance(break_key, str) or not break_key:
        raise ValueError("LoopNode config.break_key must be a non-empty string")

    iteration_key = raw.get("iteration_key", "loop_iteration")
    if not isinstance(iteration_key, str) or not iteration_key:
        raise ValueError("LoopNode config.iteration_key must be a non-empty string")

    output_key = raw.get("output_key", "loop_output")
    if not isinstance(output_key, str) or not output_key:
        raise ValueError("LoopNode config.output_key must be a non-empty string")

    return LoopNodeConfig(
        workflow_id=workflow_id,
        version=version,
        max_iterations=max_iterations,
        break_key=break_key,
        iteration_key=iteration_key,
        output_key=output_key,
    )
