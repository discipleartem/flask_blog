"""Flask application factory."""

from __future__ import annotations

from datetime import datetime

from flask import Flask

from app.config import Config
from app.db import init_app as init_db_app
from app.db import init_db


def create_app(config_object: type[Config] | None = None) -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)
    cfg = config_object or Config
    app.config.from_object(cfg)

    init_db_app(app)

    from app.auth import bp as auth_bp
    from app.auth.helpers import load_logged_in_user
    from app.comments import bp as comments_bp
    from app.posts import bp as posts_bp
    from app.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)

    app.before_request(load_logged_in_user)

    @app.context_processor
    def inject_template_globals() -> dict[str, int]:
        """Глобальные переменные шаблонов."""
        return {"current_year": datetime.now().year}

    with app.app_context():
        init_db(app)

    return app
