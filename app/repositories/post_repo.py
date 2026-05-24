"""Репозиторий для работы с постами.

Применяемые паттерны:
- Repository (Хранилище) — инкапсулирует логику доступа к данным
- Data Mapper — преобразование строк БД в объекты

Применяемые принципы:
- Single Responsibility — только работа с постами
- Explicit is better than implicit — явные SQL запросы
- Type safety — строгие типы возвращаемых значений
"""

from datetime import datetime
from typing import List, Optional

from ..db import execute_insert, execute_query, execute_update
from ..models.posts import Post


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Преобразует строку даты из БД в datetime объект."""
    if dt_str is None:
        return None
    # SQLite возвращает даты в формате ISO 8601
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


class PostRepository:
    """Репозиторий для доступа к данным постов.
    
    Предоставляет методы для CRUD операций с постами,
    включая загрузку информации об авторах.
    """
    
    def find_by_id(self, post_id: int) -> Optional[Post]:
        """Находит пост по ID с информацией об авторе.
        
        Args:
            post_id: ID поста
            
        Returns:
            Объект Post или None если не найден
        """
        query = """
        SELECT p.id, p.user_id, p.title, p.body, p.created_at, p.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE p.id = ?
        GROUP BY p.id
        """
        result = execute_query(query, (post_id,), fetch_one=True)
        
        if result:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            return Post(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                body=result['body'],
                created_at=parse_datetime(result['created_at']),
                updated_at=parse_datetime(result['updated_at']),
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles
            )
        return None
    
    def find_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Post]:
        """Находит все посты с информацией об авторах.
        
        Args:
            limit: Максимальное количество постов
            offset: Смещение для пагинации
            
        Returns:
            Список постов отсортированных по дате создания (убывание)
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT p.id, p.user_id, p.title, p.body, p.created_at, p.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        ORDER BY p.created_at DESC
        {limit_clause}
        OFFSET ?
        """
        results = execute_query(query, (offset,), fetch_all=True)
        
        posts = []
        for result in results:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            posts.append(Post(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                body=result['body'],
                created_at=parse_datetime(result['created_at']),
                updated_at=parse_datetime(result['updated_at']),
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles
            ))
        return posts
    
    def find_by_user_id(self, user_id: int, limit: Optional[int] = None) -> List[Post]:
        """Находит все посты указанного пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество постов
            
        Returns:
            Список постов пользователя отсортированных по дате создания
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT p.id, p.user_id, p.title, p.body, p.created_at, p.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
        {limit_clause}
        """
        results = execute_query(query, (user_id,), fetch_all=True)
        
        posts = []
        for result in results:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            posts.append(Post(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                body=result['body'],
                created_at=parse_datetime(result['created_at']),
                updated_at=parse_datetime(result['updated_at']),
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles
            ))
        return posts
    
    def find_grouped_by_users(self, limit_per_user: int = 3) -> List[Post]:
        """Находит посты сгруппированные по пользователям.
        
        Args:
            limit_per_user: Максимум постов на одного пользователя
            
        Returns:
            Список постов сгруппированных по пользователям
        """
        # Используем оконную функцию для группировки
        query = """
        WITH ranked_posts AS (
            SELECT p.id, p.user_id, p.title, p.body, p.created_at, p.updated_at,
                   u.login as author_login, u.discriminator as author_discriminator,
                   GROUP_CONCAT(r.name) as author_roles,
                   ROW_NUMBER() OVER (PARTITION BY p.user_id ORDER BY p.created_at DESC) as rn
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            GROUP BY p.id
        )
        SELECT id, user_id, title, body, created_at, updated_at,
               author_login, author_discriminator, author_roles
        FROM ranked_posts
        WHERE rn <= ?
        ORDER BY author_login, created_at DESC
        """
        results = execute_query(query, (limit_per_user,), fetch_all=True)
        
        posts = []
        for result in results:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            posts.append(Post(
                id=result['id'],
                user_id=result['user_id'],
                title=result['title'],
                body=result['body'],
                created_at=parse_datetime(result['created_at']),
                updated_at=parse_datetime(result['updated_at']),
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles
            ))
        return posts
    
    def create_post(self, user_id: int, title: str, body: str) -> int:
        """Создает новый пост.
        
        Args:
            user_id: ID автора
            title: Заголовок поста
            body: Содержание поста
            
        Returns:
            ID созданного поста
        """
        query = """
        INSERT INTO posts (user_id, title, body, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        return execute_insert(
            query,
            (user_id, title, body, now, now)
        )
    
    def update_post(self, post_id: int, title: str, body: str) -> bool:
        """Обновляет пост.
        
        Args:
            post_id: ID поста
            title: Новый заголовок
            body: Новое содержание
            
        Returns:
            True если пост обновлен
        """
        query = """
        UPDATE posts SET title = ?, body = ?, updated_at = ?
        WHERE id = ?
        """
        affected_rows = execute_update(
            query,
            (title, body, datetime.utcnow(), post_id)
        )
        return affected_rows > 0
    
    def delete_post(self, post_id: int) -> bool:
        """Удаляет пост.
        
        Args:
            post_id: ID поста
            
        Returns:
            True если пост удален
        """
        # Сначала удаляем комментарии к посту
        execute_update("DELETE FROM comments WHERE post_id = ?", (post_id,))
        
        # Затем удаляем пост
        query = "DELETE FROM posts WHERE id = ?"
        affected_rows = execute_update(query, (post_id,))
        return affected_rows > 0
    
    def count_posts(self, user_id: Optional[int] = None) -> int:
        """Подсчитывает количество постов.
        
        Args:
            user_id: ID пользователя для подсчета его постов
            
        Returns:
            Количество постов
        """
        if user_id:
            query = "SELECT COUNT(*) as count FROM posts WHERE user_id = ?"
            result = execute_query(query, (user_id,), fetch_one=True)
        else:
            query = "SELECT COUNT(*) as count FROM posts"
            result = execute_query(query, fetch_one=True)
        
        return result['count'] if result else 0