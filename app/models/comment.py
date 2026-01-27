"""Модель комментария к посту блога."""

from datetime import datetime
from typing import Optional, Dict, Any


class Comment:
    """Модель комментария к посту блога.

    Содержит только данные и базовую бизнес-логику.
    Вся логика работы с БД вынесена в CommentService.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        author_id: Optional[int] = None,
        post_id: Optional[int] = None,
        content: str = "",
        created: Optional[datetime] = None,
        author_username: str = "",
        author_discriminator: int = 0,
    ):
        self.id = id
        self.author_id = author_id
        self.post_id = post_id
        self.content = content
        self.created = created
        self.author_username = author_username
        self.author_discriminator = author_discriminator

    @property
    def author_display_name(self) -> str:
        """Возвращает отображаемое имя автора с дискриминатором."""
        return f"{self.author_username}#{self.author_discriminator:04d}"

    def is_author(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь автором комментария.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь автор комментария
        """
        return self.author_id == user_id

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует комментарий в словарь для шаблонов.

        Returns:
            Dict[str, Any]: словарь с данными комментария
        """
        return {
            "id": self.id,
            "author_id": self.author_id,
            "post_id": self.post_id,
            "content": self.content,
            "created": self.created,
            "author_username": self.author_username,
            "author_discriminator": self.author_discriminator,
            "author_display_name": self.author_display_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Создаёт экземпляр Comment из словаря.

        Args:
            data: Словарь с данными комментария

        Returns:
            Comment: созданный экземпляр
        """
        return cls(**data)

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<Comment(id={
            self.id}, post_id={
            self.post_id}, author_id={
            self.author_id})>"

    def __eq__(self, other: Any) -> bool:
        """Сравнение комментариев по ID."""
        if not isinstance(other, Comment):
            return False
        return self.id == other.id
