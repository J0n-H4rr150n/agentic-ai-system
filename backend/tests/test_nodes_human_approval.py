import asyncio

import pytest

from backend.nodes.control.human_approval import HumanApprovalNode


def test_human_approval_defaults_to_rejected() -> None:
    node = HumanApprovalNode("n1", config={})
    out = asyncio.run(node.execute({}))
    assert out["approval_result"] == "rejected"
    assert out["approval_output"]["decision"] == "rejected"
    assert out["approval_output"]["selected_port"] == "rejected"


def test_human_approval_approved_via_state_string() -> None:
    node = HumanApprovalNode("n1", config={})
    out = asyncio.run(node.execute({"approval_result": "approved"}))
    assert out["approval_result"] == "approved"
    assert out["approval_output"]["selected_port"] == "approved"


def test_human_approval_custom_keys() -> None:
    node = HumanApprovalNode(
        "n1",
        config={"decision_key": "my_decision", "output_key": "my_out", "approved_port": "yes", "rejected_port": "no"},
    )
    out = asyncio.run(node.execute({"my_decision": True}))
    assert out["my_decision"] == "approved"
    assert out["my_out"]["selected_port"] == "yes"


def test_human_approval_rejects_bad_config() -> None:
    node = HumanApprovalNode("n1", config={"decision_key": ""})
    with pytest.raises(ValueError, match="decision_key"):
        asyncio.run(node.execute({}))
