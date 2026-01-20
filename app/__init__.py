import os
from typing import Optional

from flask import Flask


def create_app(test_config: Optional[dict] = None) -> Flask:
    """Фабрика приложения Flask."""
    # Создаем экземпляр приложения
    app = Flask(__name__, instance_relative_config=True)

    # Дефолтные настройки
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'default_value_if_not_found_SECRET_KEY'),
        DATABASE=os.path.join(app.instance_path, 'flask_blog.sqlite'),
    )

    if test_config is None:
        # Загружаем настройки из config.py
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Загружаем тестовый конфиг, если он передан
        app.config.from_mapping(test_config)

    # Убеждаемся, что папка instance существует для БД
    os.makedirs(app.instance_path, exist_ok=True)

    # Инициализация базы данных
    from . import db
    db.init_app(app)

    # Регистрация Blueprint аутентификации
    from . import auth
    app.register_blueprint(auth.bp)

    # Регистрация Blueprint главных маршрутов
    from . import main
    app.register_blueprint(main.bp)

    return app
