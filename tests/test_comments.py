"""M5: comments CRUD and cascade."""

from __future__ import annotations

from app.db import query_one
from tests import BlogTestCase


class CommentsTests(BlogTestCase):
    def _make_post(self) -> int:
        self.register("author", "secret1")
        self.client.post("/posts/new", data={"title": "Post", "body": "Body"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Post",))
        assert post is not None
        return int(post["id"])

    def test_add_comment(self) -> None:
        post_id = self._make_post()
        response = self.client.post(
            f"/posts/{post_id}/comments",
            data={"body": "Nice post"},
            follow_redirects=True,
        )
        self.assertIn(b"Nice post", response.data)

    def test_edit_own_comment(self) -> None:
        post_id = self._make_post()
        self.client.post(f"/posts/{post_id}/comments", data={"body": "v1"})
        comment = query_one("SELECT id FROM comments WHERE body = ?", ("v1",))
        response = self.client.post(
            f"/comments/{comment['id']}/edit",
            data={"body": "v2"},
            follow_redirects=True,
        )
        self.assertIn(b"v2", response.data)

    def test_cannot_delete_others_comment(self) -> None:
        post_id = self._make_post()
        self.client.post(f"/posts/{post_id}/comments", data={"body": "mine"})
        comment = query_one("SELECT id FROM comments WHERE body = ?", ("mine",))
        self.client.get("/auth/logout")
        self.register("stranger", "secret1")
        response = self.client.post(f"/comments/{comment['id']}/delete")
        self.assertEqual(response.status_code, 403)

    def test_delete_post_cascades_comments(self) -> None:
        post_id = self._make_post()
        self.client.post(f"/posts/{post_id}/comments", data={"body": "bye"})
        self.client.post(f"/posts/{post_id}/delete", follow_redirects=True)
        self.assertIsNone(
            query_one("SELECT id FROM comments WHERE post_id = ?", (post_id,))
        )
