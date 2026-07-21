"""Рендер body_source в безопасный HTML для витрины."""

from __future__ import annotations

import html

import markdown
import nh3
from markupsafe import Markup

_ALLOWED_TAGS: set[str] = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}

_ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    "a": {"href", "title"},
    "code": {"class"},
}

_URL_SCHEMES: set[str] = {"http", "https", "mailto"}

_MARKDOWN_EXTENSIONS: list[str] = [
    "fenced_code",
    "tables",
    "nl2br",
    "sane_lists",
]


def _sanitize(raw_html: str) -> str:
    """Очистить HTML через nh3 (XSS allowlist)."""
    return nh3.clean(
        raw_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        url_schemes=_URL_SCHEMES,
    )


def _plaintext_to_html(source: str) -> str:
    """Экранировать plaintext и сохранить переносы строк."""
    escaped = html.escape(source, quote=True)
    return escaped.replace("\n", "<br>\n")


def render_to_html(source: str, fmt: str) -> Markup:
    """Преобразовать исходник в безопасный HTML по body_format.

    Args:
        source: Канонический текст (body_source).
        fmt: plaintext | markdown | html (иное → plaintext).

    Returns:
        Markup — уже санитизированный HTML для шаблона.
    """
    if not source:
        return Markup("")

    normalized = (fmt or "plaintext").strip().lower()
    if normalized == "markdown":
        raw = markdown.markdown(source, extensions=_MARKDOWN_EXTENSIONS)
        return Markup(_sanitize(raw))
    if normalized == "html":
        return Markup(_sanitize(source))
    return Markup(_sanitize(_plaintext_to_html(source)))


def render_content(source: str, fmt: str) -> Markup:
    """Jinja-фильтр: то же, что render_to_html."""
    return render_to_html(source or "", fmt or "plaintext")
