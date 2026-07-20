"""Shared test helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.config import TestConfig
from app.db import get_db


class BlogTestCase(unittest.TestCase):
    """Base case with temp SQLite DB per test."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmpdir.name) / "test.sqlite3"

        class LocalConfig(TestConfig):
            DATABASE = str(db_path)

        self.app = create_app(LocalConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        self.app_context.pop()
        self._tmpdir.cleanup()

    def csrf_token(self) -> str:
        """Fetch a page to seed CSRF, then read the token from the session."""
        self.client.get("/auth/login")
        with self.client.session_transaction() as sess:
            token = sess.get("_csrf_token")
        assert isinstance(token, str) and token
        return token

    def register(self, name: str = "alice", password: str = "secret1"):
        """Register a user and return the final response after redirects."""
        token = self.csrf_token()
        return self.client.post(
            "/auth/register",
            data={"name": name, "password": password, "csrf_token": token},
            follow_redirects=True,
        )

    def login(self, tag: str, password: str = "secret1"):
        token = self.csrf_token()
        return self.client.post(
            "/auth/login",
            data={"tag": tag, "password": password, "csrf_token": token},
            follow_redirects=True,
        )

    def login_admin(self):
        return self.login("admin#0001", self.app.config["ADMIN_PASSWORD"])

    def user_tag(self, name: str) -> str:
        row = get_db().execute(
            "SELECT name, discriminator FROM users WHERE name = ? COLLATE NOCASE",
            (name,),
        ).fetchone()
        assert row is not None
        return f"{row['name']}#{row['discriminator']}"
