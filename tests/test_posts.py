"""M4: posts CRUD and ACL."""

from __future__ import annotations

from app.db import query_one
from tests import BlogTestCase


class PostsTests(BlogTestCase):
    def test_create_and_list(self) -> None:
        self.register("writer", "secret1")
        response = self.client.post(
            "/posts/new",
            data={"title": "Hello", "body_source": "World body"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello", response.data)

        home = self.client.get("/")
        self.assertIn(b"Hello", home.data)
        self.assertIn(b"writer#", home.data)

    def test_edit_own_post(self) -> None:
        self.register("writer", "secret1")
        self.client.post("/posts/new", data={"title": "T1", "body_source": "B1"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("T1",))
        response = self.client.post(
            f"/posts/{post['id']}/edit",
            data={"title": "T2", "body_source": "B2"},
            follow_redirects=True,
        )
        self.assertIn(b"T2", response.data)

    def test_cannot_edit_others(self) -> None:
        self.register("owner", "secret1")
        self.client.post("/posts/new", data={"title": "Mine", "body_source": "Secret"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Mine",))
        self.client.get("/auth/logout")
        self.register("other", "secret1")
        response = self.client.post(
            f"/posts/{post['id']}/edit",
            data={"title": "Hijack", "body_source": "Nope"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_any(self) -> None:
        self.register("owner", "secret1")
        self.client.post("/posts/new", data={"title": "Gone", "body_source": "Soon"})
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Gone",))
        self.client.get("/auth/logout")
        self.login_admin()
        response = self.client.post(
            f"/posts/{post['id']}/delete",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(query_one("SELECT id FROM posts WHERE id = ?", (post["id"],)))

    def test_markdown_rendered_on_detail(self) -> None:
        self.register("writer", "secret1")
        self.client.post(
            "/posts/new",
            data={"title": "Md", "body_source": "Hello **bold**"},
        )
        post = query_one("SELECT id, body_format FROM posts WHERE title = ?", ("Md",))
        self.assertEqual(post["body_format"], "markdown")
        detail = self.client.get(f"/posts/{post['id']}")
        self.assertIn(b"<strong>bold</strong>", detail.data)
        self.assertNotIn(b"**bold**", detail.data)

    def test_client_body_format_ignored(self) -> None:
        self.register("writer", "secret1")
        self.client.post(
            "/posts/new",
            data={
                "title": "Fmt",
                "body_source": "plain-looking",
                "body_format": "html",
            },
        )
        post = query_one(
            "SELECT body_format FROM posts WHERE title = ?",
            ("Fmt",),
        )
        self.assertEqual(post["body_format"], "markdown")

    def test_xss_not_in_detail(self) -> None:
        self.register("writer", "secret1")
        self.client.post(
            "/posts/new",
            data={
                "title": "Xss",
                "body_source": "<script>alert(1)</script> **ok**",
            },
        )
        post = query_one("SELECT id FROM posts WHERE title = ?", ("Xss",))
        detail = self.client.get(f"/posts/{post['id']}")
        self.assertNotIn(b"<script>", detail.data)
        self.assertIn(b"<strong>ok</strong>", detail.data)

    def test_markdown_preview_endpoint(self) -> None:
        self.register("writer", "secret1")
        response = self.client.post(
            "/markdown/preview",
            json={"source": "Hello **bold**"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("<strong>bold</strong>", payload["html"])
        self.assertNotIn("**bold**", payload["html"])

    def test_markdown_preview_requires_login(self) -> None:
        response = self.client.post(
            "/markdown/preview",
            json={"source": "x"},
        )
        self.assertIn(response.status_code, (302, 401))

    def test_detail_has_open_graph_meta(self) -> None:
        self.register("writer", "secret1")
        self.client.post(
            "/posts/new",
            data={
                "title": "OG Title",
                "body_source": (
                    "Hello **world** and some more text for description.\n\n"
                    "![hero](https://cdn.example.com/cover.jpg)"
                ),
            },
        )
        post = query_one("SELECT id FROM posts WHERE title = ?", ("OG Title",))
        detail = self.client.get(f"/posts/{post['id']}")
        html = detail.data.decode("utf-8")
        self.assertEqual(detail.status_code, 200)
        self.assertIn('property="og:type" content="article"', html)
        self.assertIn('property="og:title" content="OG Title"', html)
        self.assertIn(
            'property="og:description" content="Hello world and some more text for description."',
            html,
        )
        self.assertIn(
            'property="og:image" content="https://cdn.example.com/cover.jpg"',
            html,
        )
        self.assertIn(f'property="og:url" content="http://localhost/posts/{post["id"]}"', html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_detail_og_image_falls_back_to_default(self) -> None:
        self.register("writer", "secret1")
        self.client.post(
            "/posts/new",
            data={"title": "No Img", "body_source": "Just text, no pictures."},
        )
        post = query_one("SELECT id FROM posts WHERE title = ?", ("No Img",))
        detail = self.client.get(f"/posts/{post['id']}")
        html = detail.data.decode("utf-8")
        self.assertIn(
            'property="og:image" content="http://localhost/static/img/og-default.jpg"',
            html,
        )

    def test_index_has_open_graph_meta(self) -> None:
        home = self.client.get("/")
        html = home.data.decode("utf-8")
        self.assertIn('property="og:type" content="website"', html)
        self.assertIn(
            'property="og:image" content="http://localhost/static/img/og-default.jpg"',
            html,
        )
