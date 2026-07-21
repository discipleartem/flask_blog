"""Unit tests for content_render (Markdown / plaintext / XSS)."""

from __future__ import annotations

import unittest

from app.content_render import render_to_html


class ContentRenderTests(unittest.TestCase):
    def test_markdown_bold(self) -> None:
        html = str(render_to_html("Hello **world**", "markdown"))
        self.assertIn("<strong>world</strong>", html)
        self.assertNotIn("**", html)

    def test_plaintext_escapes_and_breaks(self) -> None:
        html = str(render_to_html("a <b>x</b>\nline", "plaintext"))
        self.assertIn("&lt;b&gt;", html)
        self.assertIn("<br>", html)
        self.assertNotIn("<b>", html)

    def test_html_format_sanitized(self) -> None:
        html = str(render_to_html("<p>ok</p><script>alert(1)</script>", "html"))
        self.assertIn("<p>ok</p>", html)
        self.assertNotIn("<script>", html)

    def test_markdown_strips_script_and_js_href(self) -> None:
        src = 'Click <script>alert(1)</script> [x](javascript:alert(1))'
        html = str(render_to_html(src, "markdown"))
        self.assertNotIn("<script>", html)
        self.assertNotIn("javascript:", html)

    def test_empty_source(self) -> None:
        self.assertEqual(str(render_to_html("", "markdown")), "")

    def test_unknown_format_as_plaintext(self) -> None:
        html = str(render_to_html("**x**", "unknown"))
        self.assertIn("**x**", html)
        self.assertNotIn("<strong>", html)


if __name__ == "__main__":
    unittest.main()
