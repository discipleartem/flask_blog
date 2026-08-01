"""Модуль PythonAnywhere в админке: формы, чекбоксы, мониторинг."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError

from app.admin import pythonanywhere as pa
from app.config import Config
from app.db import query_one
from tests import BlogTestCase


class PaModuleTests(BlogTestCase):
    def test_settings_default_row(self) -> None:
        settings = pa.get_settings()
        self.assertFalse(settings.enabled)
        self.assertFalse(settings.has_credentials)
        self.assertEqual(settings.api_host, "www.pythonanywhere.com")
        self.assertFalse(settings.monitor_disk)
        self.assertEqual(settings.disk_quota_mib, Config.PA_DISC_FREE)

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

    def test_save_disk_monitoring_settings(self) -> None:
        self.login_admin()
        response = self.client.post(
            "/admin/modules/pythonanywhere",
            data=self.csrf_data(
                enabled="on",
                username="demo_user",
                api_host="www.pythonanywhere.com",
                api_token="tok-disk",
                monitor_disk="on",
                disk_quota_mib="1024",
            ),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        settings = pa.get_settings()
        self.assertTrue(settings.monitor_disk)
        self.assertEqual(settings.disk_quota_mib, 1024)
        self.assertFalse(settings.monitor_cpu)

    def test_fetch_disk_on_host(self) -> None:
        pa.save_settings(
            enabled=True,
            username="u1",
            api_host="www.pythonanywhere.com",
            webapp_domain="",
            api_token="secret",
            keep_existing_token=False,
            monitor_cpu=False,
            monitor_webapps=False,
            monitor_schedule=False,
            monitor_always_on=False,
            monitor_consoles=False,
            monitor_disk=True,
            disk_quota_mib=Config.PA_DISC_FREE,
        )
        with mock.patch(
            "app.admin.pythonanywhere._home_disk_usage_bytes",
            return_value=(256 * 1024 * 1024, None),
        ):
            data = pa.fetch_monitoring()
        self.assertEqual(len(data["blocks"]), 1)
        block = data["blocks"][0]
        self.assertEqual(block["key"], "disk")
        self.assertTrue(block["result"].ok)
        view = block["view"]
        self.assertEqual(view["kind"], "disk")
        self.assertEqual(view["percent"], 50.0)
        self.assertEqual(view["quota_mib"], Config.PA_DISC_FREE)

    def test_fetch_disk_off_host_shows_quota_note(self) -> None:
        pa.save_settings(
            enabled=True,
            username="u1",
            api_host="www.pythonanywhere.com",
            webapp_domain="",
            api_token="secret",
            keep_existing_token=False,
            monitor_cpu=False,
            monitor_webapps=False,
            monitor_schedule=False,
            monitor_always_on=False,
            monitor_consoles=False,
            monitor_disk=True,
            disk_quota_mib=Config.PA_DISC_FREE,
        )
        with mock.patch(
            "app.admin.pythonanywhere._home_disk_usage_bytes",
            return_value=(None, "Каталог недоступен"),
        ):
            data = pa.fetch_monitoring()
        view = data["blocks"][0]["view"]
        self.assertIsNone(view["used_mib"])
        self.assertEqual(view["quota_mib"], Config.PA_DISC_FREE)
        self.assertIn("недоступен", view["note"])
        self.assertTrue(data["blocks"][0]["result"].ok)

    def test_home_disk_usage_uses_pa_disk_quota_formula(self) -> None:
        """Команда измерения совпадает со справкой PA Disk Quota."""
        home = Path("/home/u1")

        class _Completed:
            returncode = 0
            stdout = "123456789\n"
            stderr = ""

        with (
            mock.patch.object(Path, "is_dir", return_value=True),
            mock.patch("app.admin.pythonanywhere.subprocess.run", return_value=_Completed()) as run,
        ):
            used, err = pa._home_disk_usage_bytes("u1")
        self.assertIsNone(err)
        self.assertEqual(used, 123456789)
        args = run.call_args
        self.assertEqual(args.args[0][0], "bash")
        script = args.args[0][2]
        self.assertIn("du -s -B 1 /tmp", script)
        self.assertIn('"$HOME"/.[!.]*', script)
        self.assertIn('"$HOME"/*', script)
        self.assertIn("awk", script)
        self.assertEqual(args.kwargs["env"]["HOME"], str(home))

    def test_settings_form_shows_disk_limit_field(self) -> None:
        self.login_admin()
        page = self.client.get("/admin/modules/pythonanywhere")
        self.assertEqual(page.status_code, 200)
        self.assertIn("disk_quota_mib".encode(), page.data)
        self.assertIn("Лимит диска".encode(), page.data)
        self.assertIn(str(Config.PA_DISC_FREE).encode(), page.data)

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
            monitor_disk=False,
            disk_quota_mib=Config.PA_DISC_FREE,
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
            monitor_disk=False,
            disk_quota_mib=Config.PA_DISC_FREE,
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
            monitor_disk=False,
            disk_quota_mib=Config.PA_DISC_FREE,
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
