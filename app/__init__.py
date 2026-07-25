"""Flask application factory."""

from __future__ import annotations

from datetime import datetime

from flask import Flask
from flask.helpers import get_debug_flag

from app.config import (
    INSECURE_DEFAULT_ADMIN_PASSWORD,
    INSECURE_DEFAULT_SECRET_KEY,
    Config,
)
from app.db import init_app as init_db_app
from app.db import init_db


def _assert_secure_production_secrets(app: Flask) -> None:
    """Запретить старт с известными небезопасными дефолтами вне debug/testing.

    Локальный ``flask run --debug`` выставляет ``FLASK_DEBUG`` до factory —
    дефолты остаются удобны для разработки. WSGI / prod без debug — hard fail.
    """
    if app.config.get("TESTING") or get_debug_flag() or app.debug:
        return

    problems: list[str] = []
    if app.config.get("SECRET_KEY") == INSECURE_DEFAULT_SECRET_KEY:
        problems.append(
            f"SECRET_KEY={INSECURE_DEFAULT_SECRET_KEY!r} — задайте уникальный "
            "ключ в .env"
        )
    if app.config.get("ADMIN_PASSWORD") == INSECURE_DEFAULT_ADMIN_PASSWORD:
        problems.append(
            f"ADMIN_PASSWORD={INSECURE_DEFAULT_ADMIN_PASSWORD!r} — задайте "
            "сильный пароль в .env"
        )
    if not problems:
        return

    message = "Отказ старта в non-debug: " + "; ".join(problems)
    app.logger.critical(message)
    raise RuntimeError(message)


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    cfg = config_object or Config
    app.config.from_object(cfg)
    _assert_secure_production_secrets(app)

    init_db_app(app)

    from app.auth import bp as auth_bp
    from app.auth.helpers import load_logged_in_user
    from app.comments import bp as comments_bp
    from app.deploy import bp as deploy_bp
    from app.posts import bp as posts_bp
    from app.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(deploy_bp)

    app.before_request(load_logged_in_user)

    from app.content_render import plain_excerpt, render_content

    app.add_template_filter(render_content, "render_content")
    app.add_template_filter(plain_excerpt, "plain_excerpt")

    @app.context_processor
    def inject_template_globals() -> dict[str, object]:
        """Глобальные переменные шаблонов."""
        from app.csrf import ensure_csrf_token

        return {
            "current_year": datetime.now().year,
            "csrf_token": ensure_csrf_token,
        }

    with app.app_context():
        init_db(app)

    return app
