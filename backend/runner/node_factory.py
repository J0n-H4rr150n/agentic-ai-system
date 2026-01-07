"""Node factory for building runnable node instances.

The graph schema only carries node type/id/config. Many node implementations
require injected dependencies (LLM clients, browser session managers, etc.).

This factory provides a deterministic, testable construction path for the MVP.
"""

from __future__ import annotations

from typing import Any, Literal

from backend.nodes.base import BaseNode
from backend.nodes.control.end import EndNode
from backend.nodes.control.agent import AgentNode
from backend.nodes.control.loop import LoopNode
from backend.nodes.control.parallel_gate import ParallelGateNode
from backend.nodes.control.router import RouterNode
from backend.nodes.control.start import StartNode
from backend.nodes.control.input import InputNode
from backend.nodes.control.human_approval import HumanApprovalNode
from backend.nodes.http.request import HTTPRequestNode
from backend.nodes.http.fuzzer import HTTPFuzzerNode
from backend.nodes.llm.base import LLMCallNode
from backend.nodes.llm.fake_client import FakeLLMClient
from backend.nodes.code_executor import CodeExecutorNode
from backend.nodes.browser.node import BrowserNode
from backend.nodes.browser.session import BrowserSession, BrowserSessionManager
from backend.nodes.browser.httpx_page import HttpxPage
from backend.workflows.store import WORKFLOW_STORE

from backend.runner.mode_guard import GuardedNode, simulate_browser_validate, simulate_http_validate
from backend.runner.test_doubles import StubBrowserNode, StubHTTPFuzzerNode, StubHTTPRequestNode


RunMode = Literal["run", "simulate", "test"]


def build_nodes_for_graph(*, run_id: str, graph_nodes: list[Any], mode: RunMode = "run") -> dict[str, BaseNode]:
    """Build executable node instances for the given graph nodes."""

    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run_id must be a non-empty string")

    if mode not in {"run", "simulate", "test"}:
        raise ValueError("mode must be one of: run, simulate, test")

    session_manager = BrowserSessionManager()

    def session_factory() -> BrowserSession:
        return BrowserSession(context=HttpxPage())

    llm_client = FakeLLMClient()

    nodes: dict[str, BaseNode] = {}

    for node in graph_nodes:
        node_id = getattr(node, "id", None)
        node_type = getattr(node, "type", None)
        config = getattr(node, "config", None)
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("Graph node id must be a non-empty string")
        if not isinstance(node_type, str) or not node_type:
            raise ValueError("Graph node type must be a non-empty string")
        if config is None:
            config = {}
        if not isinstance(config, dict):
            raise ValueError("Graph node config must be a dict")

        created: BaseNode
        if node_type == "start":
            created = StartNode(node_id, config=config)
        elif node_type == "end":
            created = EndNode(node_id, config=config)
        elif node_type == "router":
            created = RouterNode(node_id, config=config)
        elif node_type == "http_request":
            if mode == "test":
                created = StubHTTPRequestNode(node_id, config=config)
            else:
                created = HTTPRequestNode(node_id, config=config)
                if mode == "simulate":
                    created = GuardedNode(inner=created, validate=simulate_http_validate(config))
        elif node_type == "http_fuzzer":
            if mode == "test":
                created = StubHTTPFuzzerNode(node_id, config=config)
            else:
                created = HTTPFuzzerNode(node_id, config=config)
                if mode == "simulate":
                    created = GuardedNode(inner=created, validate=simulate_http_validate(config))
        elif node_type == "llm":
            created = LLMCallNode(node_id, client=llm_client, config=config)
        elif node_type == "browser":
            if mode == "test":
                created = StubBrowserNode(node_id, config=config)
            else:
                created = BrowserNode(
                    node_id,
                    run_id=run_id,
                    session_manager=session_manager,
                    session_factory=session_factory,
                    config=config,
                )
                if mode == "simulate":
                    created = GuardedNode(inner=created, validate=simulate_browser_validate(config))
        elif node_type == "code_executor":
            created = CodeExecutorNode(node_id, config=config)
        elif node_type == "agent":
            created = AgentNode(node_id, run_id=run_id, store=WORKFLOW_STORE, mode=mode, config=config)
        elif node_type == "loop":
            created = LoopNode(node_id, run_id=run_id, store=WORKFLOW_STORE, mode=mode, config=config)
        elif node_type == "parallel_gate":
            created = ParallelGateNode(node_id, config=config)
        elif node_type == "input":
            created = InputNode(node_id, config=config)
        elif node_type == "human_approval":
            created = HumanApprovalNode(node_id, config=config)
        else:
            raise ValueError(f"Unsupported node type for node factory: {node_type}")

        nodes[node_id] = created

    return nodes
