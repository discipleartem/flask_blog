"""Сервисный слой приложения."""

from .post_service import PostService
from .comment_service import CommentService

__all__ = ["PostService", "CommentService"]
