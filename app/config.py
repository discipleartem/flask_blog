"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Известные небезопасные дефолты — запрещены вне debug/testing (см. create_app).
INSECURE_DEFAULT_SECRET_KEY = "dev-change-me"
INSECURE_DEFAULT_ADMIN_PASSWORD = "admin"


class Config:
    """Default configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", INSECURE_DEFAULT_SECRET_KEY)
    DATABASE = os.environ.get(
        "DATABASE",
        str(BASE_DIR / "instance" / "blog.sqlite3"),
    )
    ADMIN_PASSWORD = os.environ.get(
        "ADMIN_PASSWORD",
        INSECURE_DEFAULT_ADMIN_PASSWORD,
    )
    DEPLOY_SECRET = os.environ.get("DEPLOY_SECRET", "")
    SCHEMA_PATH = BASE_DIR / "schema.sql"
    MIGRATIONS_DIR = BASE_DIR / "migrations"

    # Session cookie hardening (SECURE=1 behind HTTPS in production).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"


class TestConfig(Config):
    """Isolated in-memory / temp DB for unit tests."""

    TESTING = True
    SECRET_KEY = "test-secret"
    ADMIN_PASSWORD = "admin-test"
    DEPLOY_SECRET = "test-deploy-token"
    SESSION_COOKIE_SECURE = False
