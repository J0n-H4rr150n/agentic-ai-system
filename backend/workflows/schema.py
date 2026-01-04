"""Workflow I/O schema inference.

This module provides best-effort inference of which top-level state keys a graph
reads (inputs) and writes (outputs), based on node type conventions.

Scope:
- Static heuristics only (no execution).
- Deterministic output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.models.graph import GraphDefinition, NodeDefinition
from backend.workflows.store import WorkflowStore


@dataclass(frozen=True, slots=True)
class InferredIOSchema:
    inputs: set[str] = field(default_factory=set)
    outputs: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)


def infer_workflow_io_schema(
    graph: GraphDefinition,
    *,
    store: WorkflowStore | None = None,
    max_agent_depth: int = 2,
) -> InferredIOSchema:
    """Infer best-effort input/output keys for a workflow graph.

    Args:
        graph: Graph definition to analyze.
        store: Optional workflow store for resolving nested `agent` nodes.
        max_agent_depth: Maximum recursion depth when resolving nested agents.

    Returns:
        InferredIOSchema with `inputs`, `outputs`, and `warnings`.
    """

    if max_agent_depth < 0:
        raise ValueError("max_agent_depth must be >= 0")

    schema = InferredIOSchema(inputs=set(), outputs=set(), warnings=[])

    for node in graph.nodes:
        _merge_schema(schema, _infer_node_schema(node, store=store, max_agent_depth=max_agent_depth, _depth=0))

    # Determinism for warnings.
    schema.warnings.sort()
    return schema


def _merge_schema(target: InferredIOSchema, other: InferredIOSchema) -> None:
    target.inputs.update(other.inputs)
    target.outputs.update(other.outputs)
    target.warnings.extend(other.warnings)


def _root_key(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise ValueError("path must be a non-empty string")
    return path.split(".", 1)[0]


def _infer_node_schema(
    node: NodeDefinition,
    *,
    store: WorkflowStore | None,
    max_agent_depth: int,
    _depth: int,
) -> InferredIOSchema:
    cfg = dict(node.config or {})
    node_type = node.type

    inputs: set[str] = set()
    outputs: set[str] = set()
    warnings: list[str] = []

    if node_type == "start":
        initial_state = cfg.get("initial_state")
        if isinstance(initial_state, dict):
            outputs.update(str(k) for k in initial_state.keys() if isinstance(k, str) and k)
        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "end":
        result_key = cfg.get("result_key", "result")
        if isinstance(result_key, str) and result_key:
            outputs.add(result_key)
        include_keys = cfg.get("include_keys")
        if isinstance(include_keys, list):
            for key in include_keys:
                if isinstance(key, str) and key:
                    inputs.add(_root_key(key))
        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "router":
        output_key = cfg.get("output_key", "router_output")
        if isinstance(output_key, str) and output_key:
            outputs.add(output_key)

        conditions = cfg.get("conditions")
        if isinstance(conditions, list):
            for item in conditions:
                if not isinstance(item, dict):
                    continue
                var = item.get("var")
                if isinstance(var, str) and var:
                    inputs.add(_root_key(var))

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "llm":
        output_key = cfg.get("output_key", "llm_output")
        if isinstance(output_key, str) and output_key:
            outputs.add(output_key)

        prompt_key = cfg.get("prompt_key")
        if isinstance(prompt_key, str) and prompt_key:
            inputs.add(_root_key(prompt_key))

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "http_request":
        output_key = cfg.get("output_key", "http_output")
        if isinstance(output_key, str) and output_key:
            outputs.add(output_key)

        for key_field in ("url_key", "headers_key", "json_body_key", "form_body_key"):
            value = cfg.get(key_field)
            if isinstance(value, str) and value:
                inputs.add(_root_key(value))

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "browser":
        output_key = cfg.get("output_key", "browser_output")
        if isinstance(output_key, str) and output_key:
            outputs.add(output_key)

        action = cfg.get("action")
        if action == "navigate":
            url_key = cfg.get("url_key")
            if isinstance(url_key, str) and url_key:
                inputs.add(_root_key(url_key))
        elif action == "type":
            text_key = cfg.get("text_key")
            if isinstance(text_key, str) and text_key:
                inputs.add(_root_key(text_key))
        elif action == "click":
            # When clicking by SoM index, selector resolution reads state['som_index_to_selector'].
            selector = cfg.get("selector")
            som_index = cfg.get("som_index")
            if selector is None and isinstance(som_index, int):
                inputs.add("som_index_to_selector")

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "code_executor":
        output_key = cfg.get("output_key", "code_output")
        if isinstance(output_key, str) and output_key:
            outputs.add(output_key)

        input_keys = cfg.get("input_keys")
        if isinstance(input_keys, list):
            for key in input_keys:
                if isinstance(key, str) and key:
                    inputs.add(_root_key(key))

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    if node_type == "agent":
        outputs.add("__agent__")

        if store is None:
            warnings.append("agent node present but store not provided; cannot infer nested schema")
            return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

        workflow_id = cfg.get("workflow_id")
        version = cfg.get("version")
        if not isinstance(workflow_id, str) or not workflow_id:
            warnings.append("agent node missing config.workflow_id; cannot resolve nested workflow")
            return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)
        if version is not None and (not isinstance(version, int) or version < 1):
            warnings.append("agent node has invalid config.version; cannot resolve nested workflow")
            return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

        if _depth >= max_agent_depth:
            warnings.append(f"max agent depth reached for workflow_id={workflow_id!r}")
            return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

        try:
            _, selected = store.get(workflow_id, version=version)
        except KeyError:
            warnings.append(f"agent referenced workflow not found: workflow_id={workflow_id!r}")
            return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

        nested = InferredIOSchema(inputs=set(), outputs=set(), warnings=[])
        for child_node in selected.graph.nodes:
            _merge_schema(
                nested,
                _infer_node_schema(
                    child_node,
                    store=store,
                    max_agent_depth=max_agent_depth,
                    _depth=_depth + 1,
                ),
            )

        inputs.update(nested.inputs)
        outputs.update(nested.outputs)
        warnings.extend(nested.warnings)

        return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)

    warnings.append(f"unsupported node type for schema inference: {node_type}")
    return InferredIOSchema(inputs=inputs, outputs=outputs, warnings=warnings)
