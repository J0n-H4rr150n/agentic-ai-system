import threading

import pytest

from backend.nodes.browser.session import BrowserSession, BrowserSessionManager


def test_session_manager_creates_once_per_run_id() -> None:
    mgr = BrowserSessionManager()
    created: list[str] = []

    def factory() -> BrowserSession:
        created.append("x")
        return BrowserSession(context={"ok": True})

    s1 = mgr.get_or_create("run-1", factory)
    s2 = mgr.get_or_create("run-1", factory)

    assert s1 is s2
    assert created == ["x"]


def test_session_manager_close_invokes_close_callback() -> None:
    mgr = BrowserSessionManager()
    closed: list[str] = []

    def factory() -> BrowserSession:
        return BrowserSession(context={}, close=lambda: closed.append("closed"))

    mgr.get_or_create("run-1", factory)
    mgr.close("run-1")

    assert closed == ["closed"]
    assert mgr.get("run-1") is None


def test_session_manager_close_all_closes_everything() -> None:
    mgr = BrowserSessionManager()
    closed: list[str] = []

    mgr.get_or_create("a", lambda: BrowserSession(context={}, close=lambda: closed.append("a")))
    mgr.get_or_create("b", lambda: BrowserSession(context={}, close=lambda: closed.append("b")))

    mgr.close_all()
    assert set(closed) == {"a", "b"}


def test_session_manager_is_thread_safe_for_same_run_id() -> None:
    mgr = BrowserSessionManager()
    created: list[int] = []

    def factory() -> BrowserSession:
        created.append(1)
        return BrowserSession(context=object())

    results: list[BrowserSession] = []

    def worker() -> None:
        results.append(mgr.get_or_create("run-1", factory))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(set(id(r) for r in results)) == 1
    assert created == [1]


def test_session_manager_rejects_empty_run_id() -> None:
    mgr = BrowserSessionManager()
    with pytest.raises(ValueError, match="run_id"):
        mgr.get_or_create("", lambda: BrowserSession(context={}))
