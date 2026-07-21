"""Posts blueprint: home feed and CRUD."""

from __future__ import annotations

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth.helpers import is_owner_or_admin, login_required
from app.db import execute, query_all, query_one

bp = Blueprint("posts", __name__)

# Формы Post всегда сохраняют Markdown (клиентский body_format игнорируется).
_BODY_FORMAT = "markdown"


@bp.route("/")
def index():
    """Home: list posts newest first."""
    posts = query_all(
        """
        SELECT p.*, u.name AS author_name, u.discriminator AS author_disc
        FROM posts p
        JOIN users u ON u.id = p.author_id
        ORDER BY p.created_at DESC, p.id DESC
        """
    )
    return render_template("posts/index.html", posts=posts)


@bp.route("/posts/<int:post_id>")
def detail(post_id: int):
    """Show a single post with comments."""
    post = query_one(
        """
        SELECT p.*, u.name AS author_name, u.discriminator AS author_disc
        FROM posts p
        JOIN users u ON u.id = p.author_id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    if post is None:
        abort(404)
    comments = query_all(
        """
        SELECT c.*, u.name AS author_name, u.discriminator AS author_disc
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC, c.id ASC
        """,
        (post_id,),
    )
    return render_template("posts/detail.html", post=post, comments=comments)


@bp.route("/posts/new", methods=("GET", "POST"))
@login_required
def create():
    """Create a post."""
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body_source = (request.form.get("body_source") or "").strip()
        error = _validate_post(title, body_source)
        if error:
            flash(error, "danger")
        else:
            post_id = execute(
                """
                INSERT INTO posts (title, body_source, body_format, author_id)
                VALUES (?, ?, ?, ?)
                """,
                (title, body_source, _BODY_FORMAT, g.user["id"]),
            )
            flash("Статья опубликована.", "success")
            return redirect(url_for("posts.detail", post_id=post_id))
    return render_template("posts/form.html", post=None)


@bp.route("/posts/<int:post_id>/edit", methods=("GET", "POST"))
@login_required
def edit(post_id: int):
    """Update own post (or any as admin)."""
    post = query_one("SELECT * FROM posts WHERE id = ?", (post_id,))
    if post is None:
        abort(404)
    if not is_owner_or_admin(post["author_id"]):
        abort(403)

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body_source = (request.form.get("body_source") or "").strip()
        error = _validate_post(title, body_source)
        if error:
            flash(error, "danger")
        else:
            execute(
                """
                UPDATE posts
                SET title = ?, body_source = ?, body_format = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (title, body_source, _BODY_FORMAT, post_id),
            )
            flash("Статья обновлена.", "success")
            return redirect(url_for("posts.detail", post_id=post_id))

    return render_template("posts/form.html", post=post)


@bp.route("/posts/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id: int):
    """Delete own post (or any as admin). Comments cascade."""
    post = query_one("SELECT * FROM posts WHERE id = ?", (post_id,))
    if post is None:
        abort(404)
    if not is_owner_or_admin(post["author_id"]):
        abort(403)
    execute("DELETE FROM posts WHERE id = ?", (post_id,))
    flash("Статья удалена.", "info")
    return redirect(url_for("posts.index"))


def _validate_post(title: str, body_source: str) -> str | None:
    if not title:
        return "Укажите заголовок."
    if len(title) > 200:
        return "Заголовок: максимум 200 символов."
    if not body_source:
        return "Текст статьи не может быть пустым."
    return None
