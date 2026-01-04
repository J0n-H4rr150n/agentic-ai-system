"""Browser session management.

This module provides a lightweight, testable session manager that can share a
single browser session across multiple browser nodes within the same run.

We do not import Playwright here to keep unit tests fast and to avoid requiring
system browser binaries in CI. Provider-specific integrations should create a
session object (e.g., Playwright BrowserContext) via the supplied factory.
"""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Any, Callable


@dataclass(slots=True)
class BrowserSession:
    """Container for per-run browser resources."""

    context: Any
    close: Callable[[], None] | None = None


class BrowserSessionManager:
    """Manages per-run browser sessions.

    Design goals:
    - per-run isolation: sessions are keyed by a run_id
    - sharing: multiple nodes in the same run reuse the same session
    - deterministic lifecycle: callers can explicitly close sessions

    Thread-safe for use in background task execution.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, BrowserSession] = {}

    def get_or_create(self, run_id: str, factory: Callable[[], BrowserSession]) -> BrowserSession:
        """Get an existing session or create one atomically.

        Args:
            run_id: Unique run identifier.
            factory: Called once to create a BrowserSession if missing.

        Returns:
            The existing or newly-created BrowserSession.

        Raises:
            ValueError: If run_id is empty.
        """

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        with self._lock:
            existing = self._sessions.get(run_id)
            if existing is not None:
                return existing

            created = factory()
            self._sessions[run_id] = created
            return created

    def get(self, run_id: str) -> BrowserSession | None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        with self._lock:
            return self._sessions.get(run_id)

    def close(self, run_id: str) -> None:
        """Close and remove the session for run_id (if present)."""

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        session: BrowserSession | None
        with self._lock:
            session = self._sessions.pop(run_id, None)

        if session is not None and session.close is not None:
            session.close()

    def close_all(self) -> None:
        """Close and remove all sessions."""

        with self._lock:
            items = list(self._sessions.items())
            self._sessions.clear()

        for _, session in items:
            if session.close is not None:
                session.close()
