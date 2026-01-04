import pytest

from backend.runner.state import StateContainer, as_state_container


def test_state_container_defaults_empty() -> None:
    state = StateContainer()
    assert len(state) == 0
    assert state.to_dict() == {}


def test_state_container_set_get_and_contains() -> None:
    state = StateContainer()
    state.set("k", "v")

    assert state.get("k") == "v"
    assert state.get("missing", default=123) == 123
    assert "k" in state
    assert "missing" not in state


def test_state_container_item_access() -> None:
    state = StateContainer.from_mapping({"a": 1})
    assert state["a"] == 1

    state["b"] = 2
    assert state.get("b") == 2


def test_state_container_to_dict_returns_copy() -> None:
    state = StateContainer.from_mapping({"a": 1})
    out = state.to_dict()
    out["a"] = 999

    assert state.get("a") == 1


def test_state_container_snapshot_isolated() -> None:
    state = StateContainer.from_mapping({"a": 1})
    snap = state.snapshot()

    snap.set("a", 2)
    assert state.get("a") == 1
    assert snap.get("a") == 2


def test_state_container_update_from_mapping_and_iterable() -> None:
    state = StateContainer()
    state.update({"a": 1, "b": 2})
    assert state.to_dict() == {"a": 1, "b": 2}

    state.update([("b", 3), ("c", 4)])
    assert state.to_dict() == {"a": 1, "b": 3, "c": 4}


def test_state_container_delete() -> None:
    state = StateContainer.from_mapping({"a": 1})
    state.delete("a")
    assert "a" not in state

    with pytest.raises(KeyError):
        state.delete("a")


@pytest.mark.parametrize("bad_key", ["", 123, None])
def test_state_container_rejects_invalid_keys(bad_key: object) -> None:
    state = StateContainer()

    with pytest.raises(ValueError):
        state.set(bad_key, "x")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        state.get(bad_key)  # type: ignore[arg-type]


def test_as_state_container_coerces_mapping() -> None:
    coerced = as_state_container({"a": 1})
    assert isinstance(coerced, StateContainer)
    assert coerced.to_dict() == {"a": 1}

    already = StateContainer.from_mapping({"b": 2})
    assert as_state_container(already) is already
