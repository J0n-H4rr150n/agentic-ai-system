"""Agent node.

Executes a saved workflow (subgraph) as a single node.

Config:
  workflow_id: Required workflow id to load.
  version: Optional integer version to load (defaults to latest).

Output:
  Returns the subgraph final state mapping merged with a reserved `__agent__`
  key containing nested trace metadata.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode
from backend.runner.dependency import topological_sort
from backend.runner.executor import AsyncExecutor
from backend.runner.graph_parser import parse_graph
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer
from backend.workflows.store import WorkflowStore


class AgentNode(BaseNode):
    def __init__(
        self,
        node_id: str,
        *,
        run_id: str,
        store: WorkflowStore,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="agent")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(store, WorkflowStore):
            raise ValueError("store must be a WorkflowStore")

        self._run_id = run_id
        self._store = store
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        workflow_id = self._config.get("workflow_id")
        if not isinstance(workflow_id, str) or not workflow_id:
            raise ValueError("AgentNode config.workflow_id must be a non-empty string")

        version = self._config.get("version")
        if version is not None:
            if not isinstance(version, int) or version < 1:
                raise ValueError("AgentNode config.version must be an int >= 1 if provided")

        try:
            _, selected = self._store.get(workflow_id, version=version)
        except KeyError as exc:
            raise ValueError("Referenced workflow not found") from exc

        plan = parse_graph(selected.graph)
        topological_sort(plan)

        # Import locally to avoid circular imports (node_factory imports AgentNode).
        from backend.runner.node_factory import build_nodes_for_graph

        nodes = build_nodes_for_graph(run_id=self._run_id, graph_nodes=selected.graph.nodes)
        tracer = StepTracer()

        executor = AsyncExecutor()
        final_state = await executor.run(
            plan,
            nodes,
            state=StateContainer.from_mapping(state),
            tracer=tracer,
        )

        output = final_state.to_dict()
        output["__agent__"] = {
            "workflow_id": workflow_id,
            "version": selected.version,
            "trace": [step.model_dump() for step in tracer.steps()],
        }
        return output


NODE_TYPE = "agent"
NODE_CLASS = AgentNode
