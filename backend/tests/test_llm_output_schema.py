import pytest

from backend.nodes.llm.output_schema import parse_output_schema, validate_and_extract_fields


def test_parse_output_schema_accepts_json_string() -> None:
    schema = parse_output_schema('{"a": "string", "b": "number"}')
    assert schema is not None
    assert schema.fields == {"a": "string", "b": "number"}


def test_parse_output_schema_rejects_empty_schema() -> None:
    with pytest.raises(ValueError, match="define at least one field"):
        parse_output_schema("{}")


def test_validate_and_extract_fields_validates_types() -> None:
    schema = parse_output_schema('{"a": "string", "b": "number", "c": "array"}')
    assert schema is not None

    extracted = validate_and_extract_fields(schema=schema, output_json={"a": "x", "b": 1.5, "c": [1]})
    assert extracted == {"a": "x", "b": 1.5, "c": [1]}


def test_validate_and_extract_fields_rejects_type_mismatch() -> None:
    schema = parse_output_schema('{"a": "number"}')
    assert schema is not None

    with pytest.raises(ValueError, match="must be a number"):
        validate_and_extract_fields(schema=schema, output_json={"a": "nope"})
