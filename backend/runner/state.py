"""Run state container.

The runner needs a small, testable abstraction for state that flows through the
execution of a graph.

For MVP, the container is a thin wrapper around a dict with:
- key validation (non-empty strings)
- safe snapshot/to-dict behavior
- a minimal dict-like API

The executor story (S007) can decide whether nodes receive this container
directly, or whether it is adapted to a plain dict per node.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import Any


def _validate_key(key: str) -> None:
    if not isinstance(key, str) or not key:
        raise ValueError("State keys must be non-empty strings")


@dataclass(slots=True)
class StateContainer:
    """A small wrapper around a dict used as runner state."""

    _data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, initial: Mapping[str, Any] | None) -> StateContainer:
        """Create a new StateContainer from an optional mapping."""

        if initial is None:
            return cls()

        data: dict[str, Any] = {}
        for key, value in initial.items():
            _validate_key(key)
            data[key] = value

        return cls(_data=data)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the internal data."""

        return dict(self._data)

    def snapshot(self) -> StateContainer:
        """Return a new container with a shallow copy of state."""

        return StateContainer.from_mapping(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for key if present, else default."""

        _validate_key(key)
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a key to a value."""

        _validate_key(key)
        self._data[key] = value

    def delete(self, key: str) -> None:
        """Delete a key.

        Raises:
            KeyError: if key is not present.
        """

        _validate_key(key)
        del self._data[key]

    def update(self, values: Mapping[str, Any] | Iterable[tuple[str, Any]]) -> None:
        """Update state from a mapping or key/value iterable."""

        if isinstance(values, Mapping):
            items = values.items()
        else:
            items = values

        for key, value in items:
            _validate_key(key)
            self._data[key] = value

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str) or not key:
            return False
        return key in self._data

    def __getitem__(self, key: str) -> Any:
        _validate_key(key)
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self) -> Iterable[str]:
        return self._data.keys()

    def items(self) -> Iterable[tuple[str, Any]]:
        return self._data.items()

    def values(self) -> Iterable[Any]:
        return self._data.values()


def as_state_container(state: MutableMapping[str, Any] | StateContainer) -> StateContainer:
    """Coerce a mutable mapping into a StateContainer.

    This is intended as a small adapter for future executor work.
    """

    if isinstance(state, StateContainer):
        return state
    return StateContainer.from_mapping(state)
