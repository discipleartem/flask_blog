import os
from typing import Optional

from flask import Flask


def _configure_app(app: Flask, test_config: Optional[dict]) -> None:
    """Конфигурирует приложение Flask."""
    # Дефолтные настройки
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        DATABASE=os.path.join(app.instance_path, 'flask_blog.sqlite'),
    )

    if test_config is None:
        # Загружаем настройки из объекта Config
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)


def _ensure_instance_folder(app: Flask) -> None:
    """Создаёт папку instance, если она не существует."""
    os.makedirs(app.instance_path, exist_ok=True)


def _register_extensions(app: Flask) -> None:
    """Инициализирует расширения приложения."""
    from app.db import init_app
    init_app(app)


def _register_blueprints(app: Flask) -> None:
    """Регистрирует blueprints приложения."""
    # Регистрация Blueprints
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)


def create_app(test_config: Optional[dict] = None) -> Flask:
    """
    Фабрика приложения Flask.
    
    Args:
        test_config: Словарь с тестовой конфигурацией.
                     Если None, загружается продакшн-конфиг.
    
    Returns:
        Сконфигурированный экземпляр Flask приложения.
    """
    app = Flask(__name__, instance_relative_config=True)

    _configure_app(app, test_config)
    _ensure_instance_folder(app)
    _register_extensions(app)
    _register_blueprints(app)

    return app
