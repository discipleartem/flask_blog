import os
from dotenv import load_dotenv

from flask import Flask


def create_app(test_config=None):
    """Фабрика Flask-приложения.

    Создаёт и настраивает экземпляр Flask:
    - загружает конфигурацию (по умолчанию/из instance/config.py/из test_config),
    - готовит instance-папку,
    - регистрирует расширения (БД) и blueprint'ы (auth/main).

    Args:
        test_config: словарь с конфигом для тестов (переопределяет настройки).

    Returns:
        Flask: готовое к запуску приложение.
    """
    # Загружаем переменные из .env файла
    load_dotenv()
    
    # instance_relative_config=True означает, что конфиг и файлы instance
    # лежат вне пакета app/ (удобно для секретов и локальных настроек).
    app = Flask(__name__, instance_relative_config=True)

    # Базовые настройки приложения.
    # SECRET_KEY нужен для сессий/подписей (в проде брать только из env или instance/config.py).
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_123'),
    )

    # Загружаем конфигурацию:
    # - обычный режим: из config.py и instance/config.py (если файл существует)
    # - тестовый режим: из test_config
    if test_config is None:
        app.config.from_object('config.Config')
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Гарантируем существование папки instance/ (там будет БД и локальный конфиг).
    os.makedirs(app.instance_path, exist_ok=True)

    # Добавляем кастомные фильтры для шаблонов
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Преобразует переносы строк в HTML теги <br>."""
        if text is None:
            return ''
        import markupsafe
        return markupsafe.Markup(text.replace('\n', '<br>\n'))

    # Добавляем CSRF токен в контекст всех шаблонов
    @app.context_processor
    def inject_csrf_token():
        """Добавляет CSRF токен в контекст всех шаблонов."""
        from app.forms.csrf import generate_csrf_token
        return {'csrf_token': generate_csrf_token}

    # Импорты внутри функции предотвращают циклические ссылки при импорте пакетов.
    from app import db
    db.init_app(app)

    # Blueprint авторизации: /auth/...
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    # Главные страницы: /
    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
