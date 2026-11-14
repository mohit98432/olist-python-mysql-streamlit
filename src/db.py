"""Create a secure SQLAlchemy connection and load project data from MySQL."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_engine() -> Engine:
    """Build a MySQL engine using local environment variables, never source code secrets."""
    required = ("MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing {', '.join(missing)}. Copy .env.example to .env and fill it locally.")
    url = URL.create(
        "mysql+mysqlconnector",
        username=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.environ["MYSQL_DATABASE"],
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800)


def read_frame(engine: Engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a parameterized read query and return its rows as a DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql(text(sql), connection, params=params or {})
