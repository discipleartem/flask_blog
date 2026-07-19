"""M2: migrations and admin seed."""

from __future__ import annotations

from app.db import init_db, query_all, query_one, run_migrations, seed_admin
from tests import BlogTestCase


class DatabaseTests(BlogTestCase):
    def test_admin_seeded_once(self) -> None:
        admin = query_one(
            "SELECT * FROM users WHERE name = ? AND discriminator = ?",
            ("admin", "0001"),
        )
        self.assertIsNotNone(admin)
        self.assertEqual(admin["is_admin"], 1)

        created_again = seed_admin(self.app)
        self.assertFalse(created_again)
        admins = query_all("SELECT id FROM users WHERE is_admin = 1")
        self.assertEqual(len(admins), 1)

    def test_migrations_idempotent(self) -> None:
        first = run_migrations(self.app)
        second = run_migrations(self.app)
        self.assertEqual(second, [])
        # First run during create_app already applied; first here should be empty too
        self.assertEqual(first, [])

    def test_init_db_safe(self) -> None:
        init_db(self.app)
        rows = query_all("SELECT filename FROM schema_migrations")
        self.assertTrue(any(r["filename"] == "001_initial_schema.sql" for r in rows))
