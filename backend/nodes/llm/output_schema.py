"""Best-effort output schema enforcement for LLM nodes.

The frontend config provides `output_schema` as a JSON object like:

    {"confidence": "number", "action": "string"}

When provided, the backend forces JSON mode and validates the LLM's JSON output
contains the expected keys with compatible types.

This is intentionally lightweight (not full JSON Schema).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping


_ALLOWED_TYPES = {"string", "number", "boolean", "array", "object", "any"}


@dataclass(frozen=True, slots=True)
class OutputSchema:
    fields: dict[str, str]


def parse_output_schema(raw: Any) -> OutputSchema | None:
    """Parse `raw` into an OutputSchema.

    Args:
        raw: None/"" (no schema), a dict (already parsed), or a JSON string.

    Raises:
        ValueError: If the schema is present but invalid.
    """

    if raw is None:
        return None

    if isinstance(raw, str):
        if not raw.strip():
            return None
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("LLMCallNode config.output_schema must be valid JSON") from exc
        raw = loaded

    if not isinstance(raw, Mapping):
        raise ValueError("LLMCallNode config.output_schema must be a JSON object")

    fields: dict[str, str] = {}
    for key, type_name in raw.items():
        if not isinstance(key, str) or not key:
            raise ValueError("LLMCallNode output_schema keys must be non-empty strings")
        if not isinstance(type_name, str) or not type_name:
            raise ValueError("LLMCallNode output_schema values must be non-empty strings")
        if type_name not in _ALLOWED_TYPES:
            raise ValueError(f"LLMCallNode output_schema type for {key!r} must be one of: {sorted(_ALLOWED_TYPES)}")
        fields[key] = type_name

    if not fields:
        raise ValueError("LLMCallNode config.output_schema must define at least one field")

    return OutputSchema(fields=fields)


def validate_and_extract_fields(*, schema: OutputSchema, output_json: Any) -> dict[str, Any]:
    """Validate `output_json` against schema and return extracted fields.

    Raises:
        ValueError: If output_json is missing required fields or has type mismatches.
    """

    if not isinstance(schema, OutputSchema):
        raise TypeError("schema must be an OutputSchema")

    if not isinstance(output_json, dict):
        raise ValueError("LLMCallNode expected JSON object output when output_schema is provided")

    extracted: dict[str, Any] = {}
    for key, type_name in schema.fields.items():
        if key not in output_json:
            raise ValueError(f"LLMCallNode missing required output_schema field: {key}")
        value = output_json.get(key)

        if value is None:
            extracted[key] = None
            continue

        if type_name == "any":
            extracted[key] = value
            continue

        if type_name == "string":
            if not isinstance(value, str):
                raise ValueError(f"LLMCallNode output_schema field {key!r} must be a string")
        elif type_name == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"LLMCallNode output_schema field {key!r} must be a number")
        elif type_name == "boolean":
            if not isinstance(value, bool):
                raise ValueError(f"LLMCallNode output_schema field {key!r} must be a boolean")
        elif type_name == "array":
            if not isinstance(value, list):
                raise ValueError(f"LLMCallNode output_schema field {key!r} must be an array")
        elif type_name == "object":
            if not isinstance(value, dict):
                raise ValueError(f"LLMCallNode output_schema field {key!r} must be an object")
        else:
            raise ValueError("Unsupported schema type")

        extracted[key] = value

    return extracted
