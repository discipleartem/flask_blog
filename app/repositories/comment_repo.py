"""Репозиторий для работы с комментариями.

Применяемые паттерны:
- Repository (Хранилище) — инкапсулирует логику доступа к данным
- Data Mapper — преобразование строк БД в объекты

Применяемые принципы:
- Single Responsibility — только работа с комментариями
- Explicit is better than implicit — явные SQL запросы
- Type safety — строгие типы возвращаемых значений
"""

from datetime import datetime
from typing import List, Optional

from ..db import execute_insert, execute_query, execute_update
from ..models.comments import Comment


class CommentRepository:
    """Репозиторий для доступа к данным комментариев.
    
    Предоставляет методы для CRUD операций с комментариями,
    включая загрузку информации об авторах и постах.
    """
    
    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """Находит комментарий по ID с информацией об авторе и посте.
        
        Args:
            comment_id: ID комментария
            
        Returns:
            Объект Comment или None если не найден
        """
        query = """
        SELECT c.id, c.post_id, c.user_id, c.body, c.created_at, c.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles,
               p.title as post_title
        FROM comments c
        JOIN users u ON c.user_id = u.id
        JOIN posts p ON c.post_id = p.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE c.id = ?
        GROUP BY c.id
        """
        result = execute_query(query, (comment_id,), fetch_one=True)
        
        if result:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            return Comment(
                id=result['id'],
                post_id=result['post_id'],
                user_id=result['user_id'],
                body=result['body'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles,
                post_title=result['post_title']
            )
        return None
    
    def find_by_post_id(self, post_id: int, limit: Optional[int] = None) -> List[Comment]:
        """Находит все комментарии к посту.
        
        Args:
            post_id: ID поста
            limit: Максимальное количество комментариев
            
        Returns:
            Список комментариев отсортированных по дате создания
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT c.id, c.post_id, c.user_id, c.body, c.created_at, c.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles
        FROM comments c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE c.post_id = ?
        GROUP BY c.id
        ORDER BY c.created_at ASC
        {limit_clause}
        """
        results = execute_query(query, (post_id,), fetch_all=True)
        
        comments = []
        for result in results:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            comments.append(Comment(
                id=result['id'],
                post_id=result['post_id'],
                user_id=result['user_id'],
                body=result['body'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles
            ))
        return comments
    
    def find_by_user_id(self, user_id: int, limit: Optional[int] = None) -> List[Comment]:
        """Находит все комментарии пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество комментариев
            
        Returns:
            Список комментариев пользователя отсортированных по дате создания
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        SELECT c.id, c.post_id, c.user_id, c.body, c.created_at, c.updated_at,
               u.login as author_login, u.discriminator as author_discriminator,
               GROUP_CONCAT(r.name) as author_roles,
               p.title as post_title
        FROM comments c
        JOIN users u ON c.user_id = u.id
        JOIN posts p ON c.post_id = p.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY c.created_at DESC
        {limit_clause}
        """
        results = execute_query(query, (user_id,), fetch_all=True)
        
        comments = []
        for result in results:
            roles = result['author_roles'].split(',') if result['author_roles'] else []
            comments.append(Comment(
                id=result['id'],
                post_id=result['post_id'],
                user_id=result['user_id'],
                body=result['body'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                author_login=result['author_login'],
                author_discriminator=result['author_discriminator'],
                author_roles=roles,
                post_title=result['post_title']
            ))
        return comments
    
    def create_comment(self, post_id: int, user_id: int, body: str) -> int:
        """Создает новый комментарий.
        
        Args:
            post_id: ID поста
            user_id: ID автора
            body: Содержание комментария
            
        Returns:
            ID созданного комментария
        """
        query = """
        INSERT INTO comments (post_id, user_id, body, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        return execute_insert(
            query,
            (post_id, user_id, body, now, now)
        )
    
    def update_comment(self, comment_id: int, body: str) -> bool:
        """Обновляет комментарий.
        
        Args:
            comment_id: ID комментария
            body: Новое содержание
            
        Returns:
            True если комментарий обновлен
        """
        query = """
        UPDATE comments SET body = ?, updated_at = ?
        WHERE id = ?
        """
        affected_rows = execute_update(
            query,
            (body, datetime.utcnow(), comment_id)
        )
        return affected_rows > 0
    
    def delete_comment(self, comment_id: int) -> bool:
        """Удаляет комментарий.
        
        Args:
            comment_id: ID комментария
            
        Returns:
            True если комментарий удален
        """
        query = "DELETE FROM comments WHERE id = ?"
        affected_rows = execute_update(query, (comment_id,))
        return affected_rows > 0
    
    def count_comments(self, post_id: Optional[int] = None, user_id: Optional[int] = None) -> int:
        """Подсчитывает количество комментариев.
        
        Args:
            post_id: ID поста для подсчета комментариев к нему
            user_id: ID пользователя для подсчета его комментариев
            
        Returns:
            Количество комментариев
        """
        if post_id:
            query = "SELECT COUNT(*) as count FROM comments WHERE post_id = ?"
            result = execute_query(query, (post_id,), fetch_one=True)
        elif user_id:
            query = "SELECT COUNT(*) as count FROM comments WHERE user_id = ?"
            result = execute_query(query, (user_id,), fetch_one=True)
        else:
            query = "SELECT COUNT(*) as count FROM comments"
            result = execute_query(query, fetch_one=True)
        
        return result['count'] if result else 0