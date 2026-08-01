"""Модуль PythonAnywhere в админке: формы, чекбоксы, мониторинг."""

from __future__ import annotations

import json
from io import BytesIO
from unittest import mock
from urllib.error import HTTPError

from app.admin import pythonanywhere as pa
from app.db import query_one
from tests import BlogTestCase


class PaModuleTests(BlogTestCase):
    def test_settings_default_row(self) -> None:
        settings = pa.get_settings()
        self.assertFalse(settings.enabled)
        self.assertFalse(settings.has_credentials)
        self.assertEqual(settings.api_host, "www.pythonanywhere.com")

    def test_settings_form_requires_admin(self) -> None:
        self.register("nope", "secret1")
        response = self.client.get("/admin/modules/pythonanywhere")
        self.assertEqual(response.status_code, 302)

    def test_save_settings_via_form_only(self) -> None:
        self.login_admin()
        response = self.client.post(
            "/admin/modules/pythonanywhere",
            data=self.csrf_data(
                enabled="on",
                username="demo_user",
                api_host="eu.pythonanywhere.com",
                webapp_domain="demo_user.eu.pythonanywhere.com",
                api_token="tok-from-form-only",
                monitor_cpu="on",
                monitor_webapps="on",
            ),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("сохранены".encode(), response.data)

        settings = pa.get_settings()
        self.assertTrue(settings.enabled)
        self.assertEqual(settings.username, "demo_user")
        self.assertEqual(settings.api_host, "eu.pythonanywhere.com")
        self.assertEqual(settings.api_token, "tok-from-form-only")
        self.assertTrue(settings.monitor_cpu)
        self.assertTrue(settings.monitor_webapps)
        self.assertFalse(settings.monitor_schedule)

        # Token field empty keeps existing
        self.client.post(
            "/admin/modules/pythonanywhere",
            data=self.csrf_data(
                enabled="on",
                username="demo_user",
                api_host="eu.pythonanywhere.com",
                api_token="",
                monitor_cpu="on",
            ),
            follow_redirects=True,
        )
        self.assertEqual(pa.get_settings().api_token, "tok-from-form-only")

    def test_does_not_read_env_for_credentials(self) -> None:
        """Модуль не подставляет PA_* из environ."""
        import os

        self.login_admin()
        with mock.patch.dict(
            os.environ,
            {
                "PA_API_TOKEN": "env-stolen-token",
                "PA_USERNAME": "env-user",
                "API_TOKEN": "also-stolen",
            },
            clear=False,
        ):
            settings = pa.get_settings()
            self.assertNotEqual(settings.api_token, "env-stolen-token")
            self.assertNotEqual(settings.username, "env-user")
            page = self.client.get("/admin/modules/pythonanywhere")
            self.assertNotIn(b"env-stolen-token", page.data)
            self.assertNotIn(b"env-user", page.data)

    def test_dashboard_monitoring_section(self) -> None:
        self.login_admin()
        page = self.client.get("/admin/")
        self.assertEqual(page.status_code, 200)
        # Секция скрыта, пока модуль выключен / нет блоков.
        self.assertNotIn("Модуль PythonAnywhere выключен".encode(), page.data)
        self.assertNotIn("Мониторинг".encode(), page.data)

    def test_dashboard_shows_monitoring_when_enabled(self) -> None:
        pa.save_settings(
            enabled=True,
            username="u1",
            api_host="www.pythonanywhere.com",
            webapp_domain="",
            api_token="secret",
            keep_existing_token=False,
            monitor_cpu=True,
            monitor_webapps=False,
            monitor_schedule=False,
            monitor_always_on=False,
            monitor_consoles=False,
        )
        cpu_payload = {
            "daily_cpu_limit_seconds": 100,
            "daily_cpu_total_usage_seconds": 10,
            "next_reset_time": "tomorrow",
        }

        class _Resp:
            status = 200

            def read(self) -> bytes:
                return json.dumps(cpu_payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        self.login_admin()
        with mock.patch("app.admin.pythonanywhere.urlopen", return_value=_Resp()):
            page = self.client.get("/admin/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Мониторинг".encode(), page.data)
        self.assertIn(b"u1", page.data)

    def test_modules_catalog_tab(self) -> None:
        self.login_admin()
        page = self.client.get("/admin/modules")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Модули".encode(), page.data)
        self.assertIn("Хостинг".encode(), page.data)
        self.assertIn("Медиа".encode(), page.data)
        self.assertIn(b"PythonAnywhere", page.data)
        self.assertIn(b"/admin/modules/pythonanywhere", page.data)

    def test_fetch_monitoring_calls_selected_endpoints(self) -> None:
        pa.save_settings(
            enabled=True,
            username="u1",
            api_host="www.pythonanywhere.com",
            webapp_domain="",
            api_token="secret",
            keep_existing_token=False,
            monitor_cpu=True,
            monitor_webapps=False,
            monitor_schedule=False,
            monitor_always_on=False,
            monitor_consoles=False,
        )
        cpu_payload = {
            "daily_cpu_limit_seconds": 100,
            "daily_cpu_total_usage_seconds": 10,
            "next_reset_time": "tomorrow",
        }

        class _Resp:
            status = 200

            def read(self) -> bytes:
                return json.dumps(cpu_payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        with mock.patch("app.admin.pythonanywhere.urlopen", return_value=_Resp()):
            data = pa.fetch_monitoring()
        self.assertTrue(data["enabled"])
        self.assertEqual(len(data["blocks"]), 1)
        self.assertEqual(data["blocks"][0]["key"], "cpu")
        self.assertTrue(data["blocks"][0]["result"].ok)
        view = data["blocks"][0]["view"]
        self.assertEqual(view["kind"], "cpu")
        self.assertEqual(view["used"], 10.0)
        self.assertEqual(view["limit"], 100.0)
        self.assertEqual(view["percent"], 10.0)

    def test_api_error_surface(self) -> None:
        pa.save_settings(
            enabled=True,
            username="u1",
            api_host="www.pythonanywhere.com",
            webapp_domain="",
            api_token="bad",
            keep_existing_token=False,
            monitor_cpu=True,
            monitor_webapps=False,
            monitor_schedule=False,
            monitor_always_on=False,
            monitor_consoles=False,
        )
        err = HTTPError(
            "https://example",
            401,
            "Unauthorized",
            hdrs=None,  # type: ignore[arg-type]
            fp=BytesIO(b'{"detail":"Invalid token."}'),
        )
        with mock.patch("app.admin.pythonanywhere.urlopen", side_effect=err):
            data = pa.fetch_monitoring()
        self.assertFalse(data["blocks"][0]["result"].ok)
        self.assertIn("401", data["blocks"][0]["result"].error or "")

    def test_enable_without_token_rejected(self) -> None:
        self.login_admin()
        response = self.client.post(
            "/admin/modules/pythonanywhere",
            data=self.csrf_data(
                enabled="on",
                username="x",
                api_host="www.pythonanywhere.com",
                api_token="",
            ),
            follow_redirects=True,
        )
        self.assertIn("API token".encode(), response.data)
        self.assertFalse(pa.get_settings().enabled)
        row = query_one("SELECT enabled FROM pa_module_settings WHERE id = 1")
        self.assertEqual(row["enabled"], 0)
