"""Admin blueprint: панель управления users / posts / comments."""

from __future__ import annotations

from flask import Blueprint, abort, render_template

from app.auth.helpers import admin_required
from app.db import query_all, query_one

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    """Обзор админ-панели: счётчики и ссылки на таблицы."""
    counts = query_one(
        """
        SELECT
          (SELECT COUNT(*) FROM users) AS users,
          (SELECT COUNT(*) FROM posts) AS posts,
          (SELECT COUNT(*) FROM comments) AS comments
        """
    )
    return render_template("admin/dashboard.html", counts=counts)


@bp.route("/users")
@admin_required
def users():
    """Таблица всех пользователей с edit/delete."""
    rows = query_all(
        "SELECT id, name, discriminator, is_admin, created_at, updated_at "
        "FROM users ORDER BY id"
    )
    return render_template("admin/users.html", users=rows)


@bp.route("/posts")
@admin_required
def posts():
    """Таблица всех статей с edit/delete и drill-down к комментариям."""
    rows = query_all(
        """
        SELECT p.id, p.title, p.created_at, p.updated_at, p.author_id,
               u.name AS author_name, u.discriminator AS author_disc,
               (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id)
                 AS comments_count
        FROM posts p
        JOIN users u ON u.id = p.author_id
        ORDER BY p.created_at DESC, p.id DESC
        """
    )
    return render_template("admin/posts.html", posts=rows)


@bp.route("/posts/<int:post_id>/comments")
@admin_required
def post_comments(post_id: int):
    """Комментарии выбранной статьи с авторами; edit/delete."""
    post = query_one(
        """
        SELECT p.id, p.title, u.name AS author_name, u.discriminator AS author_disc
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
        SELECT c.id, c.body_source, c.created_at, c.updated_at, c.user_id,
               u.name AS author_name, u.discriminator AS author_disc
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC, c.id ASC
        """,
        (post_id,),
    )
    return render_template(
        "admin/post_comments.html",
        post=post,
        comments=comments,
    )
