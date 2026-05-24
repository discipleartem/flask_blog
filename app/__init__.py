"""Flask Blog Application Factory.

Применяемые паттерны:
- Factory (Фабрика) — для создания Flask приложения с разными конфигурациями
- Dependency Injection — для регистрации сервисов и расширений
"""

import os
from typing import Any

import dotenv
from flask import Flask, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    """Создаёт и настраивает Flask приложение.
    
    Args:
        config_class: Класс конфигурации приложения
        
    Returns:
        Настроенное Flask приложение
        
    Применяемые принципы:
    - Single Responsibility — фабрика только создаёт приложение
    - Dependency Injection — внедряем конфигурацию и зависимости
    """
    # Загружаем переменные окружения из .env файла
    dotenv.load_dotenv()
    
    # Создаём Flask приложение с параметрами согласно стандартам Flask 3.0
    app = Flask(
        import_name=__name__,
        static_folder='static',
        template_folder='templates',
        instance_relative_config=False
    )
    
    # Применяем конфигурацию
    config_class.init_app(app)
    app.config.from_object(config_class)
    
    # Инициализируем Flask-Limiter для защиты от bruteforce атаки
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    app.limiter = limiter
    
    if not app.debug and not app.testing:
        import logging
        if not app.logger.handlers:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.ERROR)
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.ERROR)
    
    # Инициализируем слой доступа к данным
    from . import db
    db.init_db()
    
    # Импортируем CLI команды для регистрации
    from . import cli
    cli.register_cli_commands(app)
    
    # Инициализируем сервисы
    from .repositories import UserRepository, PostRepository, CommentRepository
    from .services import JWTService, UserAuthService, PostService, CommentService
    
    # Создаем экземпляры репозиториев
    app.user_repo = UserRepository()
    app.post_repo = PostRepository()
    app.comment_repo = CommentRepository()
    
    # Создаем экземпляры сервисов
    app.jwt_service = JWTService()
    app.auth_service = UserAuthService(app.user_repo, app.jwt_service)
    app.post_service = PostService(app.post_repo)
    app.comment_service = CommentService(app.comment_repo, app.post_repo)
    # TODO: Создать CSRF сервис после реализации
    # app.csrf_service = CSRFService(app.config['SECRET_KEY'])
    
    # Регистрируем обработчики ошибок
    register_error_handlers(app)
    
    # Подключаем JWT middleware
    from . import auth
    app.before_request(auth.load_user_from_token)
    
    # TODO: Подключить CSRF middleware после создания сервиса
    # def csrf_protect():
    #     """Проверяет CSRF токен для небезопасных HTTP методов."""
    #     if not app.csrf_service.validate_request():
    #         from flask import abort, flash, redirect, url_for
    #         abort(400, description="Invalid CSRF token")
    # 
    # app.before_request(csrf_protect)
    
    # Регистрируем blueprints
    from .views import auth_bp, blog_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    
    # TODO: Добавить CSRF токен в контекст шаблонов после создания сервиса
    @app.context_processor
    def inject_csrf_token():
        """Временная заглушка для CSRF токена."""
        return {'csrf_token': lambda: 'temp_csrf_token'}
    
    @app.context_processor
    def inject_current_user():
        """Добавляет текущего пользователя в контекст шаблонов."""
        from .auth import get_current_user
        return {'current_user': get_current_user()}
    
    # Добавляем фильтр для преобразования переносов строк в HTML
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Преобразует переносы строк в HTML теги <br>."""
        if text is None:
            return ''
        return text.replace('\n', '<br>\n')
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Регистрирует обработчики ошибок согласно стандартам Flask 3.0."""
    
    @app.errorhandler(404)
    def page_not_found(error):
        """Обработка ошибки 404."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Обработка ошибки 500."""
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Обработка непредвиденных исключений."""
        return render_template('errors/500.html', error=str(e)), 500
