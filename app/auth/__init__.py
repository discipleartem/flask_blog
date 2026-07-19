"""Auth blueprint: register, login, logout."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth.helpers import (
    RESERVED_USERNAME,
    allocate_discriminator,
    format_tag,
    login_user,
    logout_user,
    parse_tag,
)
from app.db import execute, query_one

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Create a new user with Discord-style name#discriminator."""
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        password = request.form.get("password") or ""
        error: str | None = None

        if not name:
            error = "Укажите имя пользователя."
        elif name.casefold() == RESERVED_USERNAME:
            error = "Имя «admin» зарезервировано."
        elif len(name) < 2 or len(name) > 32:
            error = "Имя: от 2 до 32 символов."
        elif not name.replace("_", "").isalnum():
            error = "Имя: только буквы, цифры и подчёркивание."
        elif len(password) < 6:
            error = "Пароль: минимум 6 символов."

        discriminator: str | None = None
        if error is None:
            discriminator = allocate_discriminator(name)
            if discriminator is None:
                error = "Нет свободных discriminator для этого имени."

        if error is None and discriminator is not None:
            user_id = execute(
                """
                INSERT INTO users (name, discriminator, password_hash, is_admin)
                VALUES (?, ?, ?, 0)
                """,
                (name, discriminator, generate_password_hash(password)),
            )
            login_user(user_id)
            flash(f"Добро пожаловать, {format_tag(name, discriminator)}!", "success")
            return redirect(url_for("posts.index"))

        flash(error or "Ошибка регистрации.", "danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in with name#discriminator and password."""
    if request.method == "POST":
        tag = (request.form.get("tag") or "").strip()
        password = request.form.get("password") or ""
        parsed = parse_tag(tag)
        error: str | None = None
        user = None

        if not parsed:
            error = "Формат: username#0001."
        else:
            name, discriminator = parsed
            user = query_one(
                """
                SELECT * FROM users
                WHERE name = ? COLLATE NOCASE AND discriminator = ?
                """,
                (name, discriminator),
            )
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Неверный логин или пароль."

        if error is None and user is not None:
            login_user(user["id"])
            flash(f"С возвращением, {format_tag(user['name'], user['discriminator'])}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("posts.index"))

        flash(error or "Ошибка входа.", "danger")

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear session and redirect home."""
    logout_user()
    flash("Вы вышли.", "info")
    return redirect(url_for("posts.index"))
