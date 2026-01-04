from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.main import create_app
from backend.models.run import StepTrace
from backend.runs.store import RUN_HISTORY_STORE


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_run_history_list_filters_by_status_and_node_type() -> None:
    RUN_HISTORY_STORE.clear()

    started = _now()
    completed = _now()

    trace_a = [
        StepTrace(step_id=1, node_id="a", input={}, output={}, duration_ms=1, status="ok", error=None),
        StepTrace(step_id=2, node_id="b", input={}, output={}, duration_ms=1, status="ok", error=None),
    ]
    trace_b = [
        StepTrace(step_id=1, node_id="c", input={}, output={}, duration_ms=1, status="ok", error=None),
    ]

    RUN_HISTORY_STORE.persist_terminal(
        run_id="r1",
        workflow_id="w1",
        status="completed",
        started_at=started,
        completed_at=completed,
        trace=trace_a,
        error=None,
        checkpoint=None,
        node_id_to_type={"a": "start", "b": "end"},
    )

    RUN_HISTORY_STORE.persist_terminal(
        run_id="r2",
        workflow_id="w1",
        status="failed",
        started_at=started,
        completed_at=completed,
        trace=trace_b,
        error="boom",
        checkpoint=None,
        node_id_to_type={"c": "llm"},
    )

    client = TestClient(create_app())

    # Status filter
    completed_only = client.get("/api/runs?workflow_id=w1&status=completed")
    assert completed_only.status_code == 200
    runs = completed_only.json()["runs"]
    assert [r["run_id"] for r in runs] == ["r1"]

    # Node type filter
    llm_only = client.get("/api/runs?workflow_id=w1&node_type=llm")
    assert llm_only.status_code == 200
    runs = llm_only.json()["runs"]
    assert [r["run_id"] for r in runs] == ["r2"]

    # Combined filter
    none = client.get("/api/runs?workflow_id=w1&status=completed&node_type=llm")
    assert none.status_code == 200
    assert none.json()["runs"] == []
