"""M4: posts CRUD and ACL."""

from __future__ import annotations

from app.db import query_one
from tests import BlogTestCase


class PostsTests(BlogTestCase):
    def test_create_and_list(self) -> None:
        self.register("writer", "secret1")
        response = self.client.post(
            "/posts/new",
            data={"title": "Hello", "body": "World body"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello", response.data)

        home = self.client.get("/")
        self.assertIn(b"Hello", home.data)
        self.assertIn(b"writer#", home.data)

    def test_edit_own_post(self) -> None:
        self.register("writer", "secret1")
        self.client.post("/posts/new", data={"title": "T1", "body": "B1"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("T1",))
        response = self.client.post(
            f"/posts/{post['id']}/edit",
            data={"title": "T2", "body": "B2"},
            follow_redirects=True,
        )
        self.assertIn(b"T2", response.data)

    def test_cannot_edit_others(self) -> None:
        self.register("owner", "secret1")
        self.client.post("/posts/new", data={"title": "Mine", "body": "Secret"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Mine",))
        self.client.get("/auth/logout")
        self.register("other", "secret1")
        response = self.client.post(
            f"/posts/{post['id']}/edit",
            data={"title": "Hijack", "body": "Nope"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_any(self) -> None:
        self.register("owner", "secret1")
        self.client.post("/posts/new", data={"title": "Gone", "body": "Soon"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Gone",))
        self.client.get("/auth/logout")
        self.login_admin()
        response = self.client.post(
            f"/posts/{post['id']}/delete",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(query_one("SELECT id FROM posts WHERE id = ?", (post["id"],)))
