"""Human approval node.

The runner already supports pausing via GraphDefinition.node.interrupt.

This node's job is to:
- read an approval decision from state (typically injected via HITL state_patch)
- write a normalized approval record into state

Routing by output ports is a future runner feature; for now, we expose the
selected route as data for downstream nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

from backend.nodes.base import BaseNode


Decision = Literal["approved", "rejected"]


@dataclass(frozen=True, slots=True)
class HumanApprovalNodeConfig:
    decision_key: str = "approval_result"
    output_key: str = "approval_output"
    approved_port: str = "approved"
    rejected_port: str = "rejected"


class HumanApprovalNode(BaseNode):
    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="human_approval")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = _parse_config(self._config)

        raw = state.get(cfg.decision_key)
        decision = _normalize_decision(raw)

        selected_port = cfg.approved_port if decision == "approved" else cfg.rejected_port
        timestamp = datetime.now(timezone.utc).isoformat()

        record = {
            "decision": decision,
            "selected_port": selected_port,
            "timestamp": timestamp,
        }

        return {
            cfg.decision_key: decision,
            cfg.output_key: record,
        }


NODE_TYPE = "human_approval"
NODE_CLASS = HumanApprovalNode


def _parse_config(raw: dict[str, Any]) -> HumanApprovalNodeConfig:
    decision_key = raw.get("decision_key", "approval_result")
    if not isinstance(decision_key, str) or not decision_key:
        raise ValueError("HumanApprovalNode config.decision_key must be a non-empty string")

    output_key = raw.get("output_key", "approval_output")
    if not isinstance(output_key, str) or not output_key:
        raise ValueError("HumanApprovalNode config.output_key must be a non-empty string")

    approved_port = raw.get("approved_port", "approved")
    if not isinstance(approved_port, str) or not approved_port:
        raise ValueError("HumanApprovalNode config.approved_port must be a non-empty string")

    rejected_port = raw.get("rejected_port", "rejected")
    if not isinstance(rejected_port, str) or not rejected_port:
        raise ValueError("HumanApprovalNode config.rejected_port must be a non-empty string")

    return HumanApprovalNodeConfig(
        decision_key=decision_key,
        output_key=output_key,
        approved_port=approved_port,
        rejected_port=rejected_port,
    )


def _normalize_decision(raw: Any) -> Decision:
    if raw is True:
        return "approved"
    if raw is False:
        return "rejected"

    if isinstance(raw, str):
        lowered = raw.strip().lower()
        if lowered in {"approved", "approve", "allow", "yes", "y", "true"}:
            return "approved"
        if lowered in {"rejected", "reject", "deny", "no", "n", "false"}:
            return "rejected"

    # Default-safe behavior: reject when unknown.
    return "rejected"
