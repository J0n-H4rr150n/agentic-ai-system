from backend.nodes.llm.tracing import extract_decision_fields


def test_extract_decision_fields_handles_non_dict() -> None:
    assert extract_decision_fields(None) == (None, None, None)
    assert extract_decision_fields([1, 2, 3]) == (None, None, None)


def test_extract_decision_fields_reads_common_keys_and_coerces_confidence() -> None:
    decision, reasoning, confidence = extract_decision_fields(
        {"decision": "block", "reasoning": "bad", "confidence": "0.9"}
    )
    assert decision == "block"
    assert reasoning == "bad"
    assert confidence == 0.9
