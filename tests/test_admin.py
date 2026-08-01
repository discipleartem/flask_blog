"""Админ-панель: права доступа и базовый CRUD."""

from __future__ import annotations

from app.db import execute, query_one
from tests import BlogTestCase


class AdminPanelTests(BlogTestCase):
    def test_admin_requires_auth(self) -> None:
        for path in ("/admin/", "/admin/users", "/admin/posts"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/auth/login", response.headers["Location"])

    def test_admin_requires_admin_role(self) -> None:
        self.register("normie", "secret1")
        for path in ("/admin/", "/admin/users", "/admin/posts"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(
                    response.headers["Location"].endswith("/")
                    or "/auth/" not in response.headers["Location"]
                )

    def test_admin_dashboard_ok(self) -> None:
        self.login_admin()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Админ-панель".encode(), response.data)
        self.assertIn("Пользователи".encode(), response.data)
        self.assertIn("Статьи".encode(), response.data)

    def test_admin_users_table(self) -> None:
        self.register("listed", "secret1")
        self.logout()
        self.login_admin()
        response = self.client.get("/admin/users")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"listed#", response.data)
        self.assertIn(b"admin#0001", response.data)

    def test_admin_posts_and_comments_drilldown(self) -> None:
        self.register("author", "secret1")
        token = self.csrf_token()
        create = self.client.post(
            "/posts/new",
            data={
                "title": "Admin post",
                "body_source": "Body text",
                "csrf_token": token,
            },
            follow_redirects=False,
        )
        self.assertEqual(create.status_code, 302)
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Admin post",))
        self.assertIsNotNone(post)
        post_id = post["id"]

        token = self.csrf_token()
        self.client.post(
            f"/posts/{post_id}/comments",
            data={"body_source": "Hello admin", "csrf_token": token},
            follow_redirects=True,
        )

        self.logout()
        self.login_admin()

        posts_page = self.client.get("/admin/posts")
        self.assertEqual(posts_page.status_code, 200)
        self.assertIn(b"Admin post", posts_page.data)
        self.assertIn(b"author#", posts_page.data)

        comments_page = self.client.get(f"/admin/posts/{post_id}/comments")
        self.assertEqual(comments_page.status_code, 200)
        self.assertIn(b"Hello admin", comments_page.data)
        self.assertIn(b"author#", comments_page.data)

    def test_admin_delete_post_returns_to_admin(self) -> None:
        self.register("deleter", "secret1")
        token = self.csrf_token()
        self.client.post(
            "/posts/new",
            data={
                "title": "To delete",
                "body_source": "Gone soon",
                "csrf_token": token,
            },
        )
        post = query_one("SELECT id FROM posts WHERE title = ?", ("To delete",))
        self.assertIsNotNone(post)

        self.logout()
        self.login_admin()
        response = self.client.post(
            f"/posts/{post['id']}/delete",
            data=self.csrf_data(next="/admin/posts"),
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/admin/posts"))
        self.assertIsNone(query_one("SELECT id FROM posts WHERE id = ?", (post["id"],)))

    def test_admin_delete_comment_returns_to_admin(self) -> None:
        self.register("cauthor", "secret1")
        post_id = execute(
            """
            INSERT INTO posts (title, body_source, body_format, author_id)
            VALUES (?, ?, 'markdown', ?)
            """,
            ("C post", "body", query_one("SELECT id FROM users WHERE name = ?", ("cauthor",))["id"]),
        )
        user_id = query_one("SELECT id FROM users WHERE name = ?", ("cauthor",))["id"]
        comment_id = execute(
            """
            INSERT INTO comments (post_id, user_id, body_source, body_format)
            VALUES (?, ?, ?, 'markdown')
            """,
            (post_id, user_id, "Remove me"),
        )

        self.logout()
        self.login_admin()
        next_url = f"/admin/posts/{post_id}/comments"
        response = self.client.post(
            f"/comments/{comment_id}/delete",
            data=self.csrf_data(next=next_url),
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith(next_url))
        self.assertIsNone(
            query_one("SELECT id FROM comments WHERE id = ?", (comment_id,))
        )

    def test_admin_comments_404_for_missing_post(self) -> None:
        self.login_admin()
        response = self.client.get("/admin/posts/99999/comments")
        self.assertEqual(response.status_code, 404)
