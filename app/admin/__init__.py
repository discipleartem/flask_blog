"""Admin blueprint: панель управления users / posts / comments + модули."""

from __future__ import annotations

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.admin import pythonanywhere as pa
from app.admin.modules_registry import catalog_for_template
from app.auth.helpers import admin_required
from app.csrf import validate_csrf
from app.db import query_all, query_one

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def dashboard():
    """Обзор админ-панели: счётчики, мониторинг PA."""
    counts = query_one(
        """
        SELECT
          (SELECT COUNT(*) FROM users) AS users,
          (SELECT COUNT(*) FROM posts) AS posts,
          (SELECT COUNT(*) FROM comments) AS comments
        """
    )
    monitoring = pa.fetch_monitoring()
    return render_template(
        "admin/dashboard.html",
        counts=counts,
        monitoring=monitoring,
        pretty_json=_pretty_json,
    )


@bp.route("/modules")
@admin_required
def modules_index():
    """Вкладка «Модули»: каталог по категориям."""
    return render_template(
        "admin/modules.html",
        categories=catalog_for_template(),
    )


@bp.route("/modules/pythonanywhere", methods=("GET", "POST"))
@admin_required
def pythonanywhere_settings():
    """Подключаемый модуль: учётные данные PA и чекбоксы мониторинга.

    Все поля только из этой формы — без чтения env / GitHub Secrets.
    """
    if request.method == "POST":
        if not validate_csrf():
            abort(403)
        kwargs, form_error = pa.settings_from_form(request.form)
        if form_error:
            flash(form_error, "danger")
        else:
            save_error = pa.save_settings(**kwargs)
            if save_error:
                flash(save_error, "danger")
            else:
                flash("Настройки PythonAnywhere сохранены.", "success")
                return redirect(url_for("admin.pythonanywhere_settings"))

    settings = pa.get_settings()
    return render_template(
        "admin/pythonanywhere.html",
        settings=settings,
        allowed_hosts=sorted(pa.ALLOWED_HOSTS),
    )


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
        SELECT c.id, c.body_source, c.body_format, c.created_at, c.updated_at,
               c.user_id,
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


def _pretty_json(data: object) -> str:
    """Красивый JSON для шаблона мониторинга."""
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)
