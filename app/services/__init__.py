"""Сервисный слой приложения.

Применяемые паттерны:
- Service Layer — инкапсулирует бизнес-логику
- Dependency Injection — внедрение зависимостей
- Factory Method — создание сервисов с зависимостями
"""

from .comment_service import CommentService
from .user_auth_service import UserAuthService
from .jwt_service import JWTService
from .post_service import PostService

__all__ = ['JWTService', 'UserAuthService', 'PostService', 'CommentService']