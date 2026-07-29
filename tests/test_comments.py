"""M5: comments CRUD and cascade."""

from __future__ import annotations

from app.db import query_one
from tests import BlogTestCase


class CommentsTests(BlogTestCase):
    def _make_post(self) -> int:
        self.register("author", "secret1")
        self.client.post(
            "/posts/new",
            data=self.csrf_data(title="Post", body_source="Body"),
        )
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Post",))
        assert post is not None
        return int(post["id"])

    def test_add_comment(self) -> None:
        post_id = self._make_post()
        response = self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="Nice post"),
            follow_redirects=True,
        )
        self.assertIn(b"Nice post", response.data)

    def test_create_rejects_missing_csrf(self) -> None:
        post_id = self._make_post()
        response = self.client.post(
            f"/posts/{post_id}/comments",
            data={"body_source": "No CSRF"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(
            query_one("SELECT id FROM comments WHERE body_source = ?", ("No CSRF",))
        )

    def test_edit_own_comment(self) -> None:
        post_id = self._make_post()
        self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="v1"),
        )
        comment = query_one(
            "SELECT id FROM comments WHERE body_source = ?",
            ("v1",),
        )
        response = self.client.post(
            f"/comments/{comment['id']}/edit",
            data=self.csrf_data(body_source="v2"),
            follow_redirects=True,
        )
        self.assertIn(b"v2", response.data)

    def test_cannot_delete_others_comment(self) -> None:
        post_id = self._make_post()
        self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="mine"),
        )
        comment = query_one(
            "SELECT id FROM comments WHERE body_source = ?",
            ("mine",),
        )
        self.logout()
        self.register("stranger", "secret1")
        response = self.client.post(
            f"/comments/{comment['id']}/delete",
            data=self.csrf_data(),
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_post_cascades_comments(self) -> None:
        post_id = self._make_post()
        self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="bye"),
        )
        self.client.post(
            f"/posts/{post_id}/delete",
            data=self.csrf_data(),
            follow_redirects=True,
        )
        self.assertIsNone(
            query_one("SELECT id FROM comments WHERE post_id = ?", (post_id,))
        )

    def test_markdown_comment_rendered(self) -> None:
        post_id = self._make_post()
        self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="See **this**"),
        )
        row = query_one(
            "SELECT body_format FROM comments WHERE body_source = ?",
            ("See **this**",),
        )
        self.assertEqual(row["body_format"], "markdown")
        detail = self.client.get(f"/posts/{post_id}")
        self.assertIn(b"<strong>this</strong>", detail.data)
        self.assertNotIn(b"**this**", detail.data)

    def test_client_body_format_ignored_on_comment(self) -> None:
        post_id = self._make_post()
        self.client.post(
            f"/posts/{post_id}/comments",
            data=self.csrf_data(body_source="c1", body_format="html"),
        )
        row = query_one(
            "SELECT body_format FROM comments WHERE body_source = ?",
            ("c1",),
        )
        self.assertEqual(row["body_format"], "markdown")
