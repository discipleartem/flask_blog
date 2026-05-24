"""Репозитории для доступа к данным.

Применяемые паттерны:
- Repository (Хранилище) — инкапсулирует логику доступа к данным
- Data Mapper — преобразование строк БД в объекты
"""

from .comment_repo import CommentRepository
from .post_repo import PostRepository
from .user_repo import UserRepository

__all__ = ['UserRepository', 'PostRepository', 'CommentRepository']