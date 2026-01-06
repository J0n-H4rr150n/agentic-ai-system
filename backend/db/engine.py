from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


def create_db_engine() -> Engine:
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    # SQLAlchemy uses the full URL, including +psycopg driver.
    return create_engine(url, pool_pre_ping=True)
