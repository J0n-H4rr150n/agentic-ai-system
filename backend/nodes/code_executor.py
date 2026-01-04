"""Code Executor node.

This node evaluates a *restricted* Python expression against the current run state.

Security model:
- The expression is parsed with `ast.parse(..., mode="eval")`.
- Only a small allowlist of AST nodes is supported.
- No function calls, attribute access, imports, or comprehensions.
- State access is limited to `state[<str|int>]` subscripts.

Config:
    expression: Python expression to evaluate (required).
    output_key: Root state key to write the result to (optional, default: "code_output").

Output:
    Returns `{output_key: <evaluated value>}`.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from backend.nodes.base import BaseNode, NodeExecutionError


@dataclass(frozen=True, slots=True)
class _EvalContext:
    state: dict[str, Any]


_ALLOWED_BINOPS: tuple[type[ast.operator], ...] = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)

_ALLOWED_UNARYOPS: tuple[type[ast.unaryop], ...] = (ast.UAdd, ast.USub, ast.Not)

_ALLOWED_BOOLOPS: tuple[type[ast.boolop], ...] = (ast.And, ast.Or)

_ALLOWED_CMPOPS: tuple[type[ast.cmpop], ...] = (
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)


def _safe_eval_expr(expr: str, *, ctx: _EvalContext) -> Any:
    """Evaluate a restricted Python expression.

    Args:
        expr: Expression string.
        ctx: Evaluation context.

    Returns:
        Evaluated Python value.

    Raises:
        ValueError: If the expression is invalid or uses unsupported syntax.
        KeyError: If the expression reads a missing state key.
    """

    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("expression must be a non-empty string")

    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body, ctx=ctx)


def _eval_node(node: ast.AST, *, ctx: _EvalContext) -> Any:
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        if node.id != "state":
            raise ValueError("Only the name 'state' is allowed")
        return ctx.state

    if isinstance(node, ast.Dict):
        keys = [None if k is None else _eval_node(k, ctx=ctx) for k in node.keys]
        values = [_eval_node(v, ctx=ctx) for v in node.values]
        return dict(zip(keys, values, strict=True))

    if isinstance(node, ast.List):
        return [_eval_node(elt, ctx=ctx) for elt in node.elts]

    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(elt, ctx=ctx) for elt in node.elts)

    if isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, _ALLOWED_UNARYOPS):
            raise ValueError("Unsupported unary operator")
        operand = _eval_node(node.operand, ctx=ctx)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.Not):
            return not operand
        raise ValueError("Unsupported unary operator")

    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BINOPS):
            raise ValueError("Unsupported binary operator")
        left = _eval_node(node.left, ctx=ctx)
        right = _eval_node(node.right, ctx=ctx)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left**right
        raise ValueError("Unsupported binary operator")

    if isinstance(node, ast.BoolOp):
        if not isinstance(node.op, _ALLOWED_BOOLOPS):
            raise ValueError("Unsupported boolean operator")

        if isinstance(node.op, ast.And):
            value: Any = True
            for v in node.values:
                value = _eval_node(v, ctx=ctx)
                if not value:
                    return value
            return value

        if isinstance(node.op, ast.Or):
            value = False
            for v in node.values:
                value = _eval_node(v, ctx=ctx)
                if value:
                    return value
            return value

        raise ValueError("Unsupported boolean operator")

    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, ctx=ctx)
        for op, comparator in zip(node.ops, node.comparators, strict=True):
            if not isinstance(op, _ALLOWED_CMPOPS):
                raise ValueError("Unsupported comparison operator")
            right = _eval_node(comparator, ctx=ctx)

            ok: bool
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            elif isinstance(op, ast.In):
                ok = left in right
            elif isinstance(op, ast.NotIn):
                ok = left not in right
            else:
                raise ValueError("Unsupported comparison operator")

            if not ok:
                return False
            left = right

        return True

    if isinstance(node, ast.Subscript):
        base = _eval_node(node.value, ctx=ctx)
        if base is not ctx.state:
            raise ValueError("Only subscripting state[...] is allowed")

        # Python 3.9+ uses `slice` directly.
        index = node.slice
        if isinstance(index, ast.Slice):
            raise ValueError("Slicing is not supported")

        key = _eval_node(index, ctx=ctx)
        if not isinstance(key, (str, int)):
            raise ValueError("state[...] index must be str or int")
        return ctx.state[key]

    raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")


class CodeExecutorNode(BaseNode):
    """Evaluate a restricted expression and write result to state."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="code_executor")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        expression = self._config.get("expression")
        if not isinstance(expression, str) or not expression.strip():
            raise NodeExecutionError(self.node_id, "code_executor config.expression must be a non-empty string")

        output_key = self._config.get("output_key", "code_output")
        if not isinstance(output_key, str) or not output_key.strip():
            raise NodeExecutionError(self.node_id, "code_executor config.output_key must be a non-empty string")

        try:
            value = _safe_eval_expr(expression, ctx=_EvalContext(state=dict(state)))
        except KeyError as exc:
            raise NodeExecutionError(self.node_id, f"Missing state key: {exc!s}") from exc
        except ValueError as exc:
            raise NodeExecutionError(self.node_id, str(exc)) from exc

        return {output_key: value}


NODE_TYPE = "code_executor"
NODE_CLASS = CodeExecutorNode
