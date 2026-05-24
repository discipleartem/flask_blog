"""Конфигурация Flask приложения.

Применяемые паттерны:
- Configuration Object — инкапсуляция настроек в класс
- Environment Variable — загрузка конфигурации из окружения

Применяемые принципы:
- Explicit is better than implicit — явные настройки
- Single Responsibility — каждый класс отвечает за свою конфигурацию
"""

import os
from typing import Any


class Config:
    """Базовый класс конфигурации.
    
    Загружает настройки из переменных окружения с значениями по умолчанию.
    """
    
    # Flask настройки
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # База данных
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
    
    # Настройки сессий (для самописной авторизации)
    SESSION_COOKIE_DURATION: int = 7 * 24 * 60 * 60  # 7 дней
    SESSION_COOKIE_SECURE: bool = False  # В разработке False, в production True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'lax'
    
    # Приложение
    PORT: int = int(os.getenv('PORT', '5000'))
    
    @staticmethod
    def init_app(app: Any) -> None:
        """Инициализация приложения с конфигурацией."""
        pass


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG: bool = True


class ProductionConfig(Config):
    """Конфигурация для производства."""
    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True  # В production только HTTPS
    
    @classmethod
    def init_app(cls, app: Any) -> None:
        """Дополнительная инициализация для production."""
        Config.init_app(app)
        
        # Логирование ошибок в production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/blog.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Flask Blog startup')


class TestingConfig(Config):
    """Конфигурация для тестирования."""
    TESTING: bool = True
    DATABASE_URL: str = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED: bool = False


# Словарь конфигураций
config: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
