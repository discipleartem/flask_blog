"""Модели данных приложения.

Применяемые паттерны:
- Data Transfer Object (DTO) — контейнеры для данных
- Factory Method — создание объектов из БД данных

Применяемые принципы:
- Type safety — строгие типы данных
- Explicit is better than implicit — явные поля
"""

from .comments import Comment
from .posts import Post
from .users import User

__all__ = ['User', 'Post', 'Comment']