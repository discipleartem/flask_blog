"""Guard: insecure SECRET_KEY / ADMIN_PASSWORD rejected outside debug/testing."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import create_app
from app.config import (
    INSECURE_DEFAULT_ADMIN_PASSWORD,
    INSECURE_DEFAULT_SECRET_KEY,
    Config,
    TestConfig,
)


class _ProdLikeInsecureConfig(Config):
    """Prod-like: not TESTING, known-bad secrets, temp DB path set in setUp."""

    TESTING = False
    SECRET_KEY = INSECURE_DEFAULT_SECRET_KEY
    ADMIN_PASSWORD = INSECURE_DEFAULT_ADMIN_PASSWORD
    DATABASE = ""  # filled per test


class _ProdLikeSecureConfig(Config):
    """Prod-like with non-default secrets."""

    TESTING = False
    SECRET_KEY = "prod-unique-secret-key"
    ADMIN_PASSWORD = "prod-strong-admin-password"
    DATABASE = ""


class SecureDefaultsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._db_path = str(Path(self._tmpdir.name) / "test.sqlite3")
        # Isolate from developer's FLASK_DEBUG / .env side effects.
        self._env_patch = mock.patch.dict(os.environ, {"FLASK_DEBUG": "0"}, clear=False)
        self._env_patch.start()

    def tearDown(self) -> None:
        self._env_patch.stop()
        self._tmpdir.cleanup()

    def test_prod_like_refuses_insecure_defaults(self) -> None:
        class LocalConfig(_ProdLikeInsecureConfig):
            DATABASE = self._db_path

        with self.assertRaises(RuntimeError) as ctx:
            create_app(LocalConfig)
        message = str(ctx.exception)
        self.assertIn("SECRET_KEY", message)
        self.assertIn("ADMIN_PASSWORD", message)

    def test_prod_like_refuses_insecure_secret_only(self) -> None:
        class LocalConfig(_ProdLikeInsecureConfig):
            DATABASE = self._db_path
            ADMIN_PASSWORD = "not-the-default"

        with self.assertRaises(RuntimeError) as ctx:
            create_app(LocalConfig)
        message = str(ctx.exception)
        self.assertIn("SECRET_KEY", message)
        self.assertNotIn("ADMIN_PASSWORD=", message)

    def test_prod_like_allows_secure_secrets(self) -> None:
        class LocalConfig(_ProdLikeSecureConfig):
            DATABASE = self._db_path

        app = create_app(LocalConfig)
        self.assertFalse(app.testing)
        self.assertEqual(app.config["SECRET_KEY"], "prod-unique-secret-key")

    def test_debug_allows_insecure_defaults(self) -> None:
        class LocalConfig(_ProdLikeInsecureConfig):
            DATABASE = self._db_path

        with mock.patch.dict(os.environ, {"FLASK_DEBUG": "1"}):
            app = create_app(LocalConfig)
        self.assertEqual(app.config["SECRET_KEY"], INSECURE_DEFAULT_SECRET_KEY)

    def test_testing_config_unaffected(self) -> None:
        class LocalConfig(TestConfig):
            DATABASE = self._db_path

        app = create_app(LocalConfig)
        self.assertTrue(app.testing)
