"""Модели данных для работы с постами и комментариями."""
from datetime import datetime
from typing import Optional, List, Dict, Any

from .db import get_db


class Post:
    """Модель для работы с постами блога."""
    
    def __init__(self, id: Optional[int] = None, author_id: Optional[int] = None,
                 title: str = '', content: str = '', created: Optional[datetime] = None,
                 author_username: str = '', author_discriminator: int = 0):
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
    
    @classmethod
    def create(cls, author_id: int, title: str, content: str) -> 'Post':
        """Создаёт новый пост.
        
        Args:
            author_id: ID автора
            title: Заголовок поста
            content: Содержание поста
            
        Returns:
            Post: созданный пост
        """
        db = get_db()
        cursor = db.execute(
            'INSERT INTO post (author_id, title, content) VALUES (?, ?, ?)',
            (author_id, title, content)
        )
        db.commit()
        
        # Получаем созданный пост с информацией об авторе
        post = cls.find_by_id(cursor.lastrowid)
        return post
    
    @classmethod
    def find_by_id(cls, post_id: int) -> Optional['Post']:
        """Находит пост по ID.
        
        Args:
            post_id: ID поста
            
        Returns:
            Post или None если не найден
        """
        db = get_db()
        row = db.execute(
            '''SELECT p.id, p.author_id, p.title, p.content, p.created,
                      u.username, u.discriminator
               FROM post p
               JOIN user u ON p.author_id = u.id
               WHERE p.id = ?''',
            (post_id,)
        ).fetchone()
        
        if row is None:
            return None
            
        return cls(
            id=row['id'],
            author_id=row['author_id'],
            title=row['title'],
            content=row['content'],
            created=datetime.fromisoformat(row['created']) if row['created'] else None,
            author_username=row['username'],
            author_discriminator=row['discriminator']
        )
    
    @classmethod
    def get_all(cls) -> List['Post']:
        """Возвращает список всех постов с информацией об авторах.
        
        Returns:
            List[Post]: список постов, отсортированных по дате создания (новые первые)
        """
        db = get_db()
        rows = db.execute(
            '''SELECT p.id, p.author_id, p.title, p.content, p.created,
                      u.username, u.discriminator
               FROM post p
               JOIN user u ON p.author_id = u.id
               ORDER BY p.created DESC'''
        ).fetchall()
        
        posts = []
        for row in rows:
            posts.append(cls(
                id=row['id'],
                author_id=row['author_id'],
                title=row['title'],
                content=row['content'],
                created=datetime.fromisoformat(row['created']) if row['created'] else None,
                author_username=row['username'],
                author_discriminator=row['discriminator']
            ))
        
        return posts
    
    def update(self, title: str, content: str) -> None:
        """Обновляет заголовок и содержание поста.
        
        Args:
            title: Новый заголовок
            content: Новое содержание
        """
        db = get_db()
        db.execute(
            'UPDATE post SET title = ?, content = ? WHERE id = ?',
            (title, content, self.id)
        )
        db.commit()
        
        # Обновляем атрибуты объекта
        self.title = title
        self.content = content
    
    def delete(self) -> None:
        """Удаляет пост."""
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (self.id,))
        db.commit()
    
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
