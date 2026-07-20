"""Auth blueprint: register, login, logout."""

from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
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

_PENDING_CREDENTIALS_KEY = "_pending_register_credentials"


def _wants_json() -> bool:
    """True when the client asks for a JSON register response."""
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    best = request.accept_mimetypes.best_match(("application/json", "text/html"))
    return best == "application/json"


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
            tag = format_tag(name, discriminator)
            # One-shot payload for the success page (avoid Chrome saving name without #NNNN
            # from a classical form navigation).
            session[_PENDING_CREDENTIALS_KEY] = {
                "tag": tag,
                "password": password,
            }
            success_url = url_for("auth.register_success")
            if _wants_json():
                return jsonify({"ok": True, "redirect": success_url, "tag": tag})
            return redirect(success_url)

        if _wants_json():
            return jsonify({"ok": False, "error": error or "Ошибка регистрации."}), 400
        flash(error or "Ошибка регистрации.", "danger")

    return render_template("auth/register.html")


@bp.route("/register/success")
def register_success():
    """Show full tag + password once so the password manager can store name#NNNN."""
    pending = session.pop(_PENDING_CREDENTIALS_KEY, None)
    if not isinstance(pending, dict) or "tag" not in pending or "password" not in pending:
        flash("Сначала создайте аккаунт.", "info")
        return redirect(url_for("auth.register"))
    return render_template(
        "auth/register_success.html",
        tag=pending["tag"],
        password=pending["password"],
    )


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
