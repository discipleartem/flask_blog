"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Default configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")
    DATABASE = os.environ.get("DATABASE", str(BASE_DIR / "instance" / "blog.sqlite3"))
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
    SCHEMA_PATH = BASE_DIR / "schema.sql"
    MIGRATIONS_DIR = BASE_DIR / "migrations"


class TestConfig(Config):
    """Isolated in-memory / temp DB for unit tests."""

    TESTING = True
    SECRET_KEY = "test-secret"
    ADMIN_PASSWORD = "admin-test"
