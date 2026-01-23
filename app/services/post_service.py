"""Сервис для работы с постами блога."""
from datetime import datetime
from typing import Optional, List

from app.db.db import get_db
from app.models.post import Post


class PostService:
    """Сервисный слой для работы с постами.
    
    Вся логика работы с базой данных инкапсулирована здесь.
    Модель Post содержит только данные и базовую бизнес-логику.
    """
    
    @staticmethod
    def create(author_id: int, title: str, content: str) -> Post:
        """Создаёт новый пост.
        
        Args:
            author_id: ID автора
            title: Заголовок поста
            content: Содержание поста
            
        Returns:
            Post: созданный пост с полной информацией
        """
        db = get_db()
        cursor = db.execute(
            'INSERT INTO post (author_id, title, content) VALUES (?, ?, ?)',
            (author_id, title, content)
        )
        db.commit()
        
        # Получаем созданный пост с информацией об авторе
        return PostService.find_by_id(cursor.lastrowid)
    
    @staticmethod
    def find_by_id(post_id: int) -> Optional[Post]:
        """Находит пост по ID с информацией об авторе.
        
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
            
        return Post(
            id=row['id'],
            author_id=row['author_id'],
            title=row['title'],
            content=row['content'],
            created=row['created'] if row['created'] else None,
            author_username=row['username'],
            author_discriminator=row['discriminator']
        )
    
    @staticmethod
    def get_all() -> List[Post]:
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
            posts.append(Post(
                id=row['id'],
                author_id=row['author_id'],
                title=row['title'],
                content=row['content'],
                created=row['created'] if row['created'] else None,
                author_username=row['username'],
                author_discriminator=row['discriminator']
            ))
        
        return posts
    
    @staticmethod
    def update(post_id: int, title: str, content: str) -> bool:
        """Обновляет заголовок и содержание поста.
        
        Args:
            post_id: ID поста
            title: Новый заголовок
            content: Новое содержание
            
        Returns:
            bool: True если обновление успешно
        """
        db = get_db()
        cursor = db.execute(
            'UPDATE post SET title = ?, content = ? WHERE id = ?',
            (title, content, post_id)
        )
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def delete(post_id: int) -> bool:
        """Удаляет пост.
        
        Args:
            post_id: ID поста
            
        Returns:
            bool: True если удаление успешно
        """
        db = get_db()
        cursor = db.execute('DELETE FROM post WHERE id = ?', (post_id,))
        db.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def exists(post_id: int) -> bool:
        """Проверяет существование поста.
        
        Args:
            post_id: ID поста
            
        Returns:
            bool: True если пост существует
        """
        db = get_db()
        row = db.execute('SELECT 1 FROM post WHERE id = ?', (post_id,)).fetchone()
        return row is not None
