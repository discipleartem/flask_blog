"""Users blueprint: profile and admin CRUD."""

from __future__ import annotations

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from app.auth.helpers import admin_required, format_tag, login_required
from app.db import execute, query_all, query_one

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
@admin_required
def index():
    """Admin: list all users."""
    users = query_all(
        "SELECT id, name, discriminator, is_admin, created_at, updated_at FROM users ORDER BY id"
    )
    return render_template("users/index.html", users=users)


@bp.route("/<int:user_id>")
@login_required
def detail(user_id: int):
    """Show user profile (self or admin)."""
    user = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if user is None:
        abort(404)
    if g.user["id"] != user_id and not g.user["is_admin"]:
        abort(403)
    return render_template("users/detail.html", profile=user)


@bp.route("/<int:user_id>/edit", methods=("GET", "POST"))
@login_required
def edit(user_id: int):
    """Update password (self) or admin flags (admin)."""
    user = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if user is None:
        abort(404)
    if g.user["id"] != user_id and not g.user["is_admin"]:
        abort(403)

    if request.method == "POST":
        password = request.form.get("password") or ""
        if password:
            if len(password) < 6:
                flash("Пароль: минимум 6 символов.", "danger")
                return render_template("users/edit.html", profile=user)
            execute(
                """
                UPDATE users
                SET password_hash = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (generate_password_hash(password), user_id),
            )

        if g.user["is_admin"] and g.user["id"] != user_id:
            is_admin = 1 if request.form.get("is_admin") == "on" else 0
            if user["is_admin"] and not is_admin:
                admins = query_one(
                    "SELECT COUNT(*) AS c FROM users WHERE is_admin = 1"
                )
                if admins and admins["c"] <= 1:
                    flash("Нельзя снять права с последнего admin.", "danger")
                    return render_template("users/edit.html", profile=user)
            execute(
                """
                UPDATE users
                SET is_admin = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (is_admin, user_id),
            )

        flash("Профиль обновлён.", "success")
        return redirect(url_for("users.detail", user_id=user_id))

    return render_template("users/edit.html", profile=user)


@bp.route("/<int:user_id>/delete", methods=("POST",))
@admin_required
def delete(user_id: int):
    """Admin: delete a user (not the last admin)."""
    user = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if user is None:
        abort(404)
    if user["is_admin"]:
        admins = query_one("SELECT COUNT(*) AS c FROM users WHERE is_admin = 1")
        if admins and admins["c"] <= 1:
            flash("Нельзя удалить последнего admin.", "danger")
            return redirect(url_for("users.index"))
    if user["id"] == g.user["id"]:
        flash("Нельзя удалить свой аккаунт через админ-панель.", "danger")
        return redirect(url_for("users.index"))

    tag = format_tag(user["name"], user["discriminator"])
    execute("DELETE FROM users WHERE id = ?", (user_id,))
    flash(f"Пользователь {tag} удалён.", "info")
    return redirect(url_for("users.index"))
