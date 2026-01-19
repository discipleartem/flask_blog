import os

from flask import Flask, render_template


def create_app(test_config=None):
    # Создаем экземпляр приложения
    app = Flask(__name__, instance_relative_config=True)

    # Дефолтные настройки
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask_blog.sqlite'),
    )

    if test_config is None:
        # Загружаем настройки из config.py, который теперь в папке app/
        # Мы используем относительный путь от папки instance
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Загружаем тестовый конфиг, если он передан
        app.config.from_mapping(test_config)

    # Убеждаемся, что папка instance существует для БД
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Инициализация базы данных
    from . import db
    db.init_app(app)

    # Регистрация Blueprint аутентификации
    from . import auth
    app.register_blueprint(auth.bp)

    # Временный главный маршрут (будет заменен на blog blueprint позже)
    @app.route('/')
    def index():
        return render_template('index.html')

    return app
