"""Контроллеры (views) приложения.

Применяемые паттерны:
- Controller — обработка HTTP запросов
- Blueprint — организация маршрутов
- Dependency Injection — доступ к сервисам

Применяемые принципы:
- Single Responsibility — каждый blueprint отвечает за свою область
- Explicit is better than implicit — явные маршруты и ответы
"""

from .auth import auth_bp
from .blog import blog_bp

__all__ = ['auth_bp', 'blog_bp']