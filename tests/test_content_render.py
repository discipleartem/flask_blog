"""Unit tests for content_render (Markdown / plaintext / XSS)."""

from __future__ import annotations

import unittest

from app.content_render import (
    first_markdown_image_url,
    plain_excerpt,
    render_to_html,
)


class ContentRenderTests(unittest.TestCase):
    def test_markdown_bold(self) -> None:
        html = str(render_to_html("Hello **world**", "markdown"))
        self.assertIn("<strong>world</strong>", html)
        self.assertNotIn("**", html)

    def test_fenced_code_keeps_language_class(self) -> None:
        src = "```python\nprint(1)\n```"
        html = str(render_to_html(src, "markdown"))
        self.assertIn('class="language-python"', html)
        self.assertIn("print(1)", html)
        self.assertNotIn("```", html)

    def test_markdown_gfm_table(self) -> None:
        src = "| Col A | Col B |\n| --- | --- |\n| one | two |\n"
        html = str(render_to_html(src, "markdown"))
        self.assertIn("<table>", html)
        self.assertIn("<thead>", html)
        self.assertIn("<th>Col A</th>", html)
        self.assertIn("<td>one</td>", html)
        self.assertIn("<td>two</td>", html)
        self.assertNotIn("| Col A |", html)

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

    def test_plain_excerpt_strips_markdown_and_truncates(self) -> None:
        src = "# Title\n\nHello **world** and [link](https://example.com). " + ("word " * 40)
        excerpt = plain_excerpt(src, max_chars=80)
        self.assertNotIn("**", excerpt)
        self.assertNotIn("#", excerpt)
        self.assertNotIn("https://", excerpt)
        self.assertIn("Hello", excerpt)
        self.assertIn("world", excerpt)
        self.assertTrue(excerpt.endswith("…"))
        self.assertLessEqual(len(excerpt), 81)

    def test_plain_excerpt_empty(self) -> None:
        self.assertEqual(plain_excerpt(""), "")
        self.assertEqual(plain_excerpt("```\ncode\n```"), "")

    def test_plain_excerpt_strips_gfm_table(self) -> None:
        src = (
            "## 1. Архитектура\n\n"
            "| Слой | Реализация |\n"
            "| --- | --- |\n"
            "| Аутентификация | Cookie session |\n"
            "| CSRF | Свой токен |\n"
        )
        excerpt = plain_excerpt(src, max_chars=200)
        self.assertEqual(excerpt, "1. Архитектура")
        self.assertNotIn("|", excerpt)
        self.assertNotIn("---", excerpt)

    def test_first_markdown_image_url_absolute(self) -> None:
        src = "Intro\n\n![cover](https://cdn.example.com/a.jpg)\n\nMore"
        self.assertEqual(
            first_markdown_image_url(src),
            "https://cdn.example.com/a.jpg",
        )

    def test_first_markdown_image_url_skips_relative(self) -> None:
        src = "![local](/static/x.png)\n![ok](http://example.com/y.png)"
        self.assertEqual(
            first_markdown_image_url(src),
            "http://example.com/y.png",
        )

    def test_first_markdown_image_url_none(self) -> None:
        self.assertIsNone(first_markdown_image_url(""))
        self.assertIsNone(first_markdown_image_url("no images here"))
        self.assertIsNone(first_markdown_image_url("![x](relative.png)"))


if __name__ == "__main__":
    unittest.main()
