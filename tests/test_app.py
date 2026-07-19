"""M1: app factory and home page."""

from __future__ import annotations

from tests import BlogTestCase


class AppFactoryTests(BlogTestCase):
    def test_create_app(self) -> None:
        self.assertTrue(self.app.testing)

    def test_home_ok(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flask Blog", response.data)

    def test_login_page_ok(self) -> None:
        response = self.client.get("/auth/login")
        self.assertEqual(response.status_code, 200)

    def test_register_page_ok(self) -> None:
        response = self.client.get("/auth/register")
        self.assertEqual(response.status_code, 200)
