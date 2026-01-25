"""Модель поста блога."""
from datetime import datetime
from typing import Optional, Dict, Any


class Post:
    """Модель поста блога.
    
    Содержит только данные и базовую бизнес-логику.
    Вся логика работы с БД вынесена в PostService.
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        author_id: Optional[int] = None,
        title: str = '',
        content: str = '',
        created: Optional[datetime] = None,
        author_username: str = '',
        author_discriminator: int = 0
    ):
        self.id = id
        self.author_id = author_id
        self.title = title
        self.content = content
        self.created = created
        self.author_username = author_username
        self.author_discriminator = author_discriminator
    
    @property
    def author_display_name(self) -> str:
        """Возвращает отображаемое имя автора с дискриминатором."""
        return f"{self.author_username}#{self.author_discriminator:04d}"
    
    def is_author(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь автором поста.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если пользователь автор поста
        """
        return self.author_id == user_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует пост в словарь для шаблонов.
        
        Returns:
            Dict[str, Any]: словарь с данными поста
        """
        return {
            'id': self.id,
            'author_id': self.author_id,
            'title': self.title,
            'content': self.content,
            'created': self.created,
            'author_username': self.author_username,
            'author_discriminator': self.author_discriminator,
            'author_display_name': self.author_display_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """Создаёт экземпляр Post из словаря.
        
        Args:
            data: Словарь с данными поста
            
        Returns:
            Post: созданный экземпляр
        """
        return cls(**data)
    
    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        return f"<Post(id={self.id}, title='{self.title}', author_id={self.author_id})>"
    
    def __eq__(self, other) -> bool:
        """Сравнение постов по ID."""
        if not isinstance(other, Post):
            return False
        return self.id == other.id
