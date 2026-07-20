"""M3: auth and users."""

from __future__ import annotations

from app.db import query_one
from tests import BlogTestCase


class AuthTests(BlogTestCase):
    def test_register_and_login(self) -> None:
        response = self.register("bob", "secret1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"bob#", response.data)
        self.assertIn(b'autocomplete="username"', response.data)
        self.assertNotIn(b'value="secret1"', response.data)
        self.assertNotIn(b"PasswordCredential", response.data)

        self.client.get("/auth/logout", follow_redirects=True)
        tag = self.user_tag("bob")
        response = self.login(tag, "secret1")
        self.assertIn(b"bob#", response.data)

    def test_register_form_uses_nickname_autocomplete(self) -> None:
        response = self.client.get("/auth/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'autocomplete="nickname"', response.data)
        self.assertNotIn(b'autocomplete="username"', response.data)

    def test_register_json_stores_tag_only_server_side(self) -> None:
        token = self.csrf_token()
        response = self.client.post(
            "/auth/register",
            data={"name": "jsonbob", "password": "secret1", "csrf_token": token},
            headers={
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-Token": token,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        self.assertIn("/auth/register/success", payload["redirect"])
        self.assertTrue(payload["tag"].startswith("jsonbob#"))
        self.assertNotIn("password", payload)

        success = self.client.get(payload["redirect"])
        self.assertEqual(success.status_code, 200)
        self.assertIn(payload["tag"].encode(), success.data)
        self.assertNotIn(b'type="password"', success.data)
        self.assertNotIn(b"PasswordCredential", success.data)

    def test_register_rejects_missing_csrf(self) -> None:
        response = self.client.post(
            "/auth/register",
            data={"name": "nocsrf", "password": "secret1"},
            headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["ok"])

    def test_reserved_admin_name(self) -> None:
        response = self.register("admin", "secret1")
        self.assertIn("зарезервировано".encode(), response.data)
        row = query_one(
            "SELECT id FROM users WHERE name = ? COLLATE NOCASE AND is_admin = 0",
            ("admin",),
        )
        self.assertIsNone(row)

    def test_login_admin(self) -> None:
        response = self.login_admin()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"admin#0001", response.data)

    def test_logout(self) -> None:
        self.register("carol", "secret1")
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertIn("Вы вышли".encode(), response.data)
        self.assertNotIn(b"carol#", response.data)

    def test_profile_self(self) -> None:
        self.register("dave", "secret1")
        user = query_one("SELECT id FROM users WHERE name = ?", ("dave",))
        response = self.client.get(f"/users/{user['id']}")
        self.assertEqual(response.status_code, 200)

    def test_users_list_admin_only(self) -> None:
        self.register("eve", "secret1")
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 302)

        self.client.get("/auth/logout")
        self.login_admin()
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"eve#", response.data)
